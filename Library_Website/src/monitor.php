<?php
/**
 * Eviulon reader activity: private, server-side-only request logging.
 * No client-side JavaScript, tracking cookies, raw IP addresses, or book dumps.
 * User-agent crawler IDs are claims, NOT verified crawler identities.
 */
declare(strict_types=1);

function monitor_log_dir(): string { return DATA_ROOT . 'monitor-logs'; }
function monitor_agent(string $userAgent): array {
    // Known user-agent strings are self-reported and may be spoofed.
    $patterns = [
        'Googlebot' => '/Googlebot/i',
        'GoogleOther' => '/GoogleOther/i',
        'Bingbot' => '/bingbot|BingPreview/i',
        'Applebot' => '/Applebot/i',
        'DuckDuckBot' => '/DuckDuckBot/i',
        'YandexBot' => '/YandexBot/i',
        'Baiduspider' => '/Baiduspider/i',
        'OAI-SearchBot' => '/OAI-SearchBot/i',
        'GPTBot' => '/GPTBot/i',
        'ChatGPT-User' => '/ChatGPT-User/i',
        'ClaudeBot' => '/ClaudeBot/i',
        'Claude-SearchBot' => '/Claude-SearchBot/i',
        'Claude-User' => '/Claude-User/i',
        'PerplexityBot' => '/PerplexityBot/i',
        'Perplexity-User' => '/Perplexity-User/i',
        'CCBot' => '/CCBot/i',
        'Amazonbot' => '/Amazonbot/i',
        'Bytespider' => '/Bytespider/i',
        'Meta-ExternalAgent' => '/Meta-ExternalAgent/i',
        'Meta-ExternalFetcher' => '/Meta-ExternalFetcher/i',
        'Facebook crawler' => '/facebookexternalhit|Facebot/i',
        'Twitterbot' => '/Twitterbot/i',
        'LinkedInBot' => '/LinkedInBot/i',
        'AhrefsBot' => '/AhrefsBot/i',
        'SemrushBot' => '/SemrushBot/i',
    ];
    foreach ($patterns as $label => $pattern) {
        if (preg_match($pattern, $userAgent)) return [$label, true];
    }
    if (preg_match('/bot\b|crawler|spider|crawl\b|fetcher/i', $userAgent)) return ['Other claimed crawler', true];
    return ['Other visitor / unknown', false];
}
function monitor_kind(string $path): array {
    if (preg_match('#^/([a-z0-9-]+)/([0-9]+)(?:-([0-9]+))?/$#', $path, $m)) {
        return ['kind' => isset($m[3]) ? 'page-spread' : 'print-page', 'book' => $m[1], 'from' => (int)$m[2], 'to' => isset($m[3]) ? (int)$m[3] : (int)$m[2]];
    }
    if (preg_match('#^/api/v1/books/([a-z0-9-]+)/pages/([0-9]+)/$#', $path, $m)) {
        return ['kind' => 'json-print-page', 'book' => $m[1], 'from' => (int)$m[2], 'to' => (int)$m[2]];
    }
    if ($path === '/ag-ui/') return ['kind' => 'ag-ui'];
    if (str_ends_with($path,'.xml') && str_starts_with($path,'/sitemap')) return ['kind' => 'sitemap'];
    if ($path === '/robots.txt') return ['kind' => 'robots'];
    if ($path === '/llms.txt' || $path === '/ai/knowledge.json') return ['kind' => 'machine-discovery'];
    if (str_starts_with($path, '/api/')) return ['kind' => 'api-discovery'];
    if ($path === '/search/') return ['kind' => 'search'];
    if ($path === '/index/') return ['kind' => 'page-directory'];
    if ($path === '/about/') return ['kind' => 'about'];
    if ($path === '/') return ['kind' => 'home'];
    if (preg_match('#^/([a-z0-9-]+)/$#', $path)) return ['kind' => 'book-or-other'];
    return ['kind' => 'other'];
}
function monitor_register(string $path, string $method): void {
    if (str_starts_with($path, '/admin/') || !in_array($method, ['GET','HEAD','POST'], true)) return;
    $started = microtime(true);
    $ua = substr(str_replace(["\r", "\n"], ' ', (string)($_SERVER['HTTP_USER_AGENT'] ?? '')), 0, 260);
    [$agent, $claimed] = monitor_agent($ua);
    $referer = (string)($_SERVER['HTTP_REFERER'] ?? '');
    $refhost = parse_url($referer, PHP_URL_HOST);
    if (!is_string($refhost)) $refhost = '';
    $refhost = substr($refhost, 0, 110);
    // Log the completed response, including error status. Paths only, never query strings or IP addresses.
    register_shutdown_function(static function () use ($started, $path, $method, $ua, $agent, $claimed, $refhost): void {
        $status = http_response_code();
        if (!is_int($status) || $status < 100) $status = 200;
        $record = [
            'time' => gmdate('Y-m-d\TH:i:s\Z'), 'method' => $method,
            'path' => substr($path, 0, 210), 'status' => $status,
            'kind' => monitor_kind($path)['kind'],
            'agent' => $agent, 'claimed_crawler' => $claimed,
            'user_agent' => $ua,
            'referrer_host' => $refhost,
            'ms' => round((microtime(true) - $started) * 1000, 1),
        ];
        foreach (monitor_kind($path) as $key => $val) {
            if ($key !== 'kind') $record[$key] = $val;
        }
        $directory = monitor_log_dir();
        if (!is_dir($directory) && !@mkdir($directory, 0750, true) && !is_dir($directory)) return;
        $filename = $directory . '/hits-' . gmdate('Y-m-d') . '.jsonl';
        @file_put_contents($filename, j($record) . "\n", FILE_APPEND | LOCK_EX);
        // Lazy pruning: at most once per 250 requests; retain up to 90 days of activity.
        if (random_int(1, 250) === 1) monitor_prune_logs();
    });
}
function monitor_prune_logs(): void {
    $olderThan = strtotime('-90 days');
    foreach (glob(monitor_log_dir() . '/hits-????-??-??.jsonl') ?: [] as $file) {
        if (preg_match('/hits-(\d{4}-\d{2}-\d{2})\.jsonl$/', $file, $m) && strtotime($m[1]) < $olderThan) @unlink($file);
    }
}
function monitor_settings(): array {
    $settings = [];
    $config = DATA_ROOT . 'monitor-config.php';
    if (is_file($config)) {
        $loaded = require $config;
        if (is_array($loaded)) $settings = $loaded;
    }
    $hash = getenv('EVIULON_MONITOR_PASSWORD_HASH');
    $user = getenv('EVIULON_MONITOR_USER');
    if (is_string($hash) && $hash !== '') $settings['password_hash'] = $hash;
    if (is_string($user) && $user !== '') $settings['username'] = $user;
    return $settings;
}
function monitor_require_auth(): void {
    $settings = monitor_settings();
    $hash = (string)($settings['password_hash'] ?? '');
    $expectedUser = (string)($settings['username'] ?? 'admin');
    header('Cache-Control: no-store, private');
    header('X-Robots-Tag: noindex, nofollow, noarchive');
    if ($hash === '') {
        http_response_code(503);
        header('Content-Type: text/plain; charset=utf-8');
        echo "Private crawler monitor is not configured. Set a password hash in data/monitor-config.php or EVIULON_MONITOR_PASSWORD_HASH. See README_DEPLOY.md.\n";
        exit;
    }
    $u = (string)($_SERVER['PHP_AUTH_USER'] ?? '');
    $p = (string)($_SERVER['PHP_AUTH_PW'] ?? '');
    if ($u === '' && isset($_SERVER['HTTP_AUTHORIZATION']) && preg_match('/^Basic\s+([A-Za-z0-9+\/=]+)/i', (string)$_SERVER['HTTP_AUTHORIZATION'], $m)) {
        $pair = base64_decode($m[1], true);
        if (is_string($pair) && str_contains($pair, ':')) [$u,$p] = explode(':', $pair, 2);
    }
    if (!hash_equals($expectedUser, $u) || !password_verify($p, $hash)) {
        http_response_code(401);
        header('WWW-Authenticate: Basic realm="Eviulon private crawler activity", charset="UTF-8"');
        header('Content-Type: text/plain; charset=utf-8');
        echo "Authorized library administrator only.\n";
        exit;
    }
}
function monitor_dashboard(): never {
    monitor_require_auth();
    $days = (int)($_GET['days'] ?? 7);
    if (!in_array($days, [7,30,90], true)) $days = 7;
    $filter = (string)($_GET['filter'] ?? 'bots');
    if (!in_array($filter, ['bots','all','others'], true)) $filter = 'bots';
    $counts = ['requests'=>0,'ok'=>0,'error'=>0,'individual_pages'=>0];
    $byAgent = []; $byKind = []; $byPath = []; $byDay = []; $recent = []; $unique = []; $byBook = []; $bookUnique = [];
    $dir = monitor_log_dir();
    for ($i = $days - 1; $i >= 0; $i--) {
        $day = gmdate('Y-m-d', strtotime('today UTC -' . $i . ' days'));
        $file = $dir . '/hits-' . $day . '.jsonl';
        if (!is_file($file) || !is_readable($file)) continue;
        $fh = fopen($file, 'rb');
        if ($fh === false) continue;
        while (($line = fgets($fh)) !== false) {
            $r = json_decode($line, true);
            if (!is_array($r)) continue;
            $bot = !empty($r['claimed_crawler']);
            if (($filter === 'bots' && !$bot) || ($filter === 'others' && $bot)) continue;
            $counts['requests']++;
            $status = (int)($r['status'] ?? 0);
            if ($status >= 200 && $status < 400) $counts['ok']++; else $counts['error']++;
            $agent = (string)($r['agent'] ?? 'Unknown'); $kind = (string)($r['kind'] ?? 'unknown');
            $path = (string)($r['path'] ?? '/');
            $byAgent[$agent] = ($byAgent[$agent] ?? 0) + 1;
            $byKind[$kind] = ($byKind[$kind] ?? 0) + 1;
            $byPath[$path] = ($byPath[$path] ?? 0) + 1;
            $byDay[$day] = ($byDay[$day] ?? 0) + 1;
            $slug = (string)($r['book'] ?? '');
            if ($slug !== '') $byBook[$slug] = ($byBook[$slug] ?? 0) + 1;
            if ($status === 200 && in_array($kind, ['print-page','json-print-page','page-spread'], true)) {
                $first = (int)($r['from'] ?? 0);
                $last = min((int)($r['to'] ?? $first), $first + 1);
                for ($pn = $first; $pn <= $last; $pn++) {
                    if ($slug === '' || $pn < 1) continue;
                    $key = $slug . ':' . $pn;
                    $unique[$key] = true;
                    $bookUnique[$slug][$pn] = true;
                }
            }
            $recent[] = $r;
            if (count($recent) > 100) array_shift($recent);
        }
        fclose($fh);
    }
    $counts['individual_pages'] = count($unique);
    arsort($byAgent); arsort($byKind); arsort($byPath); krsort($byDay);
    $recent = array_reverse($recent);
    $desc = 'Private server-side activity summary for claimed crawlers and other visitors. Crawler identity is unverified by user-agent alone. HTTP access does not prove indexing.';
    render_head('Private crawler activity — Eviulon', $desc, '/admin/crawlers/', [], 'noindex,nofollow,noarchive');
    echo '<main id="content" class="shell monitor-page"><p class="eyebrow">PRIVATE · PHP ACCESS LOGS · UTC</p><h1>Crawler &amp; reading activity</h1><p class="monitor-intro">'.h($desc).' Google Search Console and Bing Webmaster Tools are required to inspect actual index coverage. Sitemap and static asset requests may be visible only in your web server access logs.</p>';
    echo '<form class="monitor-filters" method="get" action="/admin/crawlers/"><label>Window <select name="days">';
    foreach ([7,30,90] as $d) echo '<option value="'.$d.'"'.($d===$days?' selected':'').'>'.$d.' days</option>';
    echo '</select></label><label>Visitor type <select name="filter">';
    foreach (['bots'=>'Claimed crawlers','all'=>'All requests','others'=>'Other visitors'] as $value=>$title) echo '<option value="'.h($value).'"'.($value===$filter?' selected':'').'>'.h($title).'</option>';
    echo '</select></label><button class="btn btn-primary" type="submit">Apply</button></form>';
    echo '<div class="monitor-metrics">';
    foreach (['Requests'=>'requests','Successful responses'=>'ok','Errors / rejected'=>'error','Distinct print pages served'=>'individual_pages'] as $label=>$key) {
        echo '<div><strong>'.number_format($counts[$key]).'</strong><span>'.h($label).'</span></div>';
    }
    echo '</div>';
    if (!is_dir($dir) || !is_writable($dir)) echo '<p class="monitor-warning"><strong>Logging may be disabled:</strong> PHP cannot write to <code>data/monitor-logs/</code>. Grant the web-server user write access to that directory; see deployment guide.</p>';
    if ($counts['requests']===0) echo '<p class="monitor-warning">No matching PHP requests recorded for this filter and period yet. This does not mean the site is not indexed.</p>';
    echo '<div class="monitor-columns"><section><h2>Crawler or visitor claim</h2><table><thead><tr><th>User-agent category</th><th>Requests</th></tr></thead><tbody>';
    foreach ($byAgent as $name=>$count) echo '<tr><td>'.h($name).'</td><td>'.number_format($count).'</td></tr>';
    echo '</tbody></table></section><section><h2>Requested resource type</h2><table><thead><tr><th>Type</th><th>Requests</th></tr></thead><tbody>';
    foreach ($byKind as $kind=>$count) echo '<tr><td>'.h($kind).'</td><td>'.number_format($count).'</td></tr>';
    echo '</tbody></table></section></div>';
    echo '<section><h2>Book-by-book crawler coverage</h2><p>Distinct print pages served in a successful individual-page, JSON-page, or two-page-spread response. These are requests, not confirmed indexed pages.</p><div class="monitor-table-scroll"><table><thead><tr><th>Book</th><th>Requests</th><th>Distinct pages served</th><th>Source total</th></tr></thead><tbody>';
    foreach (all_books() as $b) {
        $slug = $b['slug'];
        echo '<tr><td><a href="'.h(book_url($b)).'">'.h($b['title']).'</a></td><td>'.number_format($byBook[$slug] ?? 0).'</td><td>'.number_format(count($bookUnique[$slug] ?? [])).'</td><td>'.number_format($b['page_count']).'</td></tr>';
    }
    echo '</tbody></table></div></section>';
    echo '<div class="monitor-columns"><section><h2>Most requested URLs</h2><table><thead><tr><th>Public path</th><th>Requests</th></tr></thead><tbody>';
    foreach (array_slice($byPath,0,25,true) as $url=>$count) echo '<tr><td class="monitor-url"><a href="'.h($url).'">'.h($url).'</a></td><td>'.number_format($count).'</td></tr>';
    echo '</tbody></table></section><section><h2>Daily requests (UTC)</h2><table><thead><tr><th>Date</th><th>Requests</th></tr></thead><tbody>';
    foreach ($byDay as $day=>$count) echo '<tr><td>'.h($day).'</td><td>'.number_format($count).'</td></tr>';
    echo '</tbody></table></section></div>';
    echo '<section><h2>Recent server-rendered requests</h2><div class="monitor-table-scroll"><table><thead><tr><th>UTC time</th><th>Claimed visitor</th><th>URL</th><th>Response</th><th>Method</th><th>Time</th></tr></thead><tbody>';
    foreach ($recent as $r) {
        $path=(string)($r['path']??'/');
        echo '<tr><td>'.h($r['time']??'').'</td><td title="'.h($r['user_agent']??'').'">'.h($r['agent']??'').'</td><td class="monitor-url"><a href="'.h($path).'">'.h($path).'</a></td><td>'.(int)($r['status']??0).'</td><td>'.h($r['method']??'').'</td><td>'.h($r['ms']??0).' ms</td></tr>';
    }
    echo '</tbody></table></div></section><aside class="monitor-disclaimer"><h2>Interpreting these numbers</h2><p>The log records requests to PHP pages, their paths and response status, claimed user agents, and timings. It does <strong>not</strong> inspect a crawler’s internal reasoning, verify crawler ownership, guarantee that a page was read, or confirm that Google/Bing indexed it. No raw IP addresses, cookies, or search queries are stored in this built-in monitor. Logs rotate daily and are retained for up to 90 days with opportunistic pruning.</p><p>For validated search coverage, connect <a href="https://search.google.com/search-console/about">Google Search Console</a> and <a href="https://www.bing.com/webmasters/">Bing Webmaster Tools</a> and check their indexing reports. For full static asset/sitemap traffic and independently verified crawler identities, use the web host’s access logs and vendor reverse-DNS/IP verification procedures.</p></aside></main>';
    render_foot(); exit;
}
