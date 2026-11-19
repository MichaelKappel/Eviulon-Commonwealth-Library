<?php
/**
 * Eviulon private discovery observability (v3.4).
 * Only public URL paths, response codes, request classes, and claimed UA categories.
 * No IPs, referrers, raw user-agent strings, cookies, query parameters or request bodies.
 * Claimed bot identities are NEVER promoted to verified crawler events.
 */
declare(strict_types=1);

function monitor_log_dir(): string { return DATA_ROOT . 'monitor-logs'; }
function monitor_agent(string $userAgent): array {
    // Self-reported: do not trust this for crawler verification or access control.
    $patterns = [
        'Googlebot' => '/Googlebot/i', 'GoogleOther' => '/GoogleOther/i',
        'Bingbot' => '/bingbot|BingPreview/i', 'Applebot' => '/Applebot/i',
        'DuckDuckBot' => '/DuckDuckBot/i', 'YandexBot' => '/YandexBot/i',
        'Baiduspider' => '/Baiduspider/i', 'OAI-SearchBot' => '/OAI-SearchBot/i',
        'GPTBot' => '/GPTBot/i', 'ChatGPT-User' => '/ChatGPT-User/i',
        'ClaudeBot' => '/ClaudeBot/i', 'Claude-SearchBot' => '/Claude-SearchBot/i',
        'Claude-User' => '/Claude-User/i', 'PerplexityBot' => '/PerplexityBot/i',
        'Perplexity-User' => '/Perplexity-User/i', 'CCBot' => '/CCBot/i',
        'Amazonbot' => '/Amazonbot/i', 'Bytespider' => '/Bytespider/i',
        'Meta-ExternalAgent' => '/Meta-ExternalAgent/i',
        'Meta-ExternalFetcher' => '/Meta-ExternalFetcher/i',
        'Facebook crawler' => '/facebookexternalhit|Facebot/i',
        'Twitterbot' => '/Twitterbot/i', 'LinkedInBot' => '/LinkedInBot/i',
        'AhrefsBot' => '/AhrefsBot/i', 'SemrushBot' => '/SemrushBot/i',
    ];
    foreach ($patterns as $label => $pattern) if (preg_match($pattern, $userAgent)) return [$label, true];
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
    if (preg_match('#^/research/(?:eviulon|evulgare)/[a-z0-9-]+/parts/[0-9]+/$#', $path) ||
        preg_match('#^/api/v1/research/(?:eviulon|evulgare)/[a-z0-9-]+/parts/[0-9]+/$#', $path)) return ['kind'=>'research-section'];
    if ($path === '/ag-ui/') return ['kind' => 'ag-ui'];
    if (str_ends_with($path,'.xml') && str_starts_with($path,'/sitemap')) return ['kind' => 'sitemap'];
    if ($path === '/robots.txt') return ['kind' => 'robots'];
    if ($path === '/llms.txt' || $path === '/ai/knowledge.json' || $path === '/openapi.json') return ['kind' => 'machine-discovery'];
    if (str_starts_with($path, '/api/')) return ['kind' => 'api-discovery'];
    if ($path === '/search/') return ['kind' => 'search'];
    if ($path === '/index/' || $path === '/chapters/') return ['kind' => 'book-directory'];
    if ($path === '/about/') return ['kind' => 'about'];
    if ($path === '/') return ['kind' => 'home'];
    if (preg_match('#^/([a-z0-9-]+)/$#', $path)) return ['kind' => 'book-or-other'];
    return ['kind' => 'other'];
}
function monitor_source(string $path): string {
    // Neutral group for search/AG-UI: scope may be both or only research, and is not logged.
    if ($path === '/search/' || $path === '/ag-ui/' || $path === '/api/v1/search/') return 'unattributed-search-or-agent';
    if (preg_match('#^/(?:research/|api/v1/research/)#', $path)) return 'research';
    if (preg_match('#^/api/v1/books/#', $path) || in_array($path, ['/index/','/chapters/','/feeds/books.atom'],true)) return 'books';
    if (preg_match('#^/([a-z0-9-]+)/(?:(\d+)(?:-(\d+))?/)?$#',$path,$m) && find_book($m[1]) !== null) return 'books';
    return 'site-or-service';
}
function monitor_safe_path(string $path): string {
    // Retain only recognized, bounded public URL paths; suppress arbitrary injected identifiers.
    if ($path === '/' || in_array($path, ['/search/','/ag-ui/','/about/','/index/','/chapters/','/research/','/robots.txt','/llms.txt','/openapi.json','/feeds/books.atom','/for-agents/','/ai/knowledge.json'], true)) return $path;
    if (strlen($path) > 210 || !preg_match('#^/[a-z0-9][a-z0-9/._-]*$#D', $path)) return '/[other]';
    if (preg_match('#^/(?:api/v1/|research/|sitemap(?:-[a-z0-9-]+)?\.xml$)#',$path)) return $path;
    if (monitor_source($path) === 'books') return $path;
    return '/[other]';
}
function monitor_register(string $path, string $method): void {
    // Collection is opt-in: avoid per-request append/lock + shutdown work for
    // human readers, crawlers, and public APIs by default. A deployment may
    // explicitly enable the existing private, authenticated monitor with env.
    if (getenv('EVIULON_MONITOR_ENABLED') !== '1') return;
    if (str_starts_with($path, '/admin/') || !in_array($method, ['GET','HEAD','POST'], true)) return;
    $started = microtime(true);
    [$agent, $claimed] = monitor_agent(substr((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 260));
    $safePath = monitor_safe_path($path);
    $details = monitor_kind($safePath);
    $source = monitor_source($safePath);
    register_shutdown_function(static function () use ($started, $safePath, $method, $agent, $claimed, $details, $source): void {
        $status = http_response_code();
        if (!is_int($status) || $status < 100) $status = 200;
        $record = [
            'schema_version' => 2, 'time' => gmdate('Y-m-d\TH:i:s\Z'),
            'method' => $method, 'path' => $safePath, 'status' => $status,
            'kind' => $details['kind'], 'source' => $source,
            'agent' => $agent, 'claimed_crawler' => $claimed,
            'ms' => round((microtime(true) - $started) * 1000, 1),
        ];
        foreach ($details as $key => $val) if ($key !== 'kind') $record[$key] = $val;
        $directory = monitor_log_dir();
        if (!is_dir($directory) && !@mkdir($directory, 0750, true) && !is_dir($directory)) return;
        $filename = $directory . '/hits-' . gmdate('Y-m-d') . '.jsonl';
        @file_put_contents($filename, j($record) . "\n", FILE_APPEND | LOCK_EX);
        if (random_int(1,250) === 1) monitor_prune_logs();
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
    if (is_file($config)) { $loaded = require $config; if (is_array($loaded)) $settings = $loaded; }
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
    header('Pragma: no-cache');
    header('X-Robots-Tag: noindex, nofollow, noarchive');
    header('X-Content-Type-Options: nosniff');
    if ($hash === '' || $hash === 'REPLACE_WITH_GENERATED_PASSWORD_HASH') {
        http_response_code(503);
        header('Content-Type: text/plain; charset=utf-8');
        echo "Private crawler monitor is not configured. Set a password hash in data/monitor-config.php or EVIULON_MONITOR_PASSWORD_HASH.\n";
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
function monitor_parameters(): array {
    $days = (int)($_GET['days'] ?? 7);
    if (!in_array($days, [7, 30, 90], true)) $days = 7;
    $filter = (string)($_GET['filter'] ?? 'bots');
    if (!in_array($filter, ['bots','others','all'], true)) $filter = 'bots';
    return [$days, $filter];
}
function monitor_summary(int $days, string $filter): array {
    $counts=['requests'=>0,'success_2xx'=>0,'redirect_3xx'=>0,'not_modified_304'=>0,'errors_4xx'=>0,'errors_5xx'=>0,
       'successful_book_pages'=>0,'successful_research_sections'=>0,'distinct_book_pages'=>0];
    $byAgent=[]; $byKind=[]; $bySource=[]; $byDay=[]; $byBook=[]; $bookUnique=[]; $unique=[];
    $knownBooks=[];foreach(all_books() as $bookRecord)$knownBooks[$bookRecord['slug']]=$bookRecord;
    $logDays=0; $invalidLines=0; $linesRead=0; $partial=false;
    // Per-day limit explicitly discloses incomplete coverage rather than silently truncating.
    $maxLinesPerDay=120000;
    for ($i=$days-1;$i>=0;$i--) {
        $day=gmdate('Y-m-d', strtotime('today UTC -'.$i.' days'));
        $byDay[$day]=0;
        $file=monitor_log_dir().'/hits-'.$day.'.jsonl';
        if (!is_file($file) || !is_readable($file)) continue;
        $fh=@fopen($file,'rb'); if ($fh===false)continue;
        $logDays++; $readToday=0;
        while (($line=fgets($fh,65537))!==false) {
            ++$readToday;
            if ($readToday>$maxLinesPerDay) { $partial=true; break; }
            if (strlen($line)>=65536 && !str_ends_with($line,"\n")) { ++$invalidLines; $partial=true; while(!feof($fh) && !str_ends_with((string)fgets($fh,65537),"\n")) {} continue; }
            ++$linesRead;
            $r=json_decode($line,true);
            if (!is_array($r)) {++$invalidLines;continue;}
            $bot=!empty($r['claimed_crawler']);
            if (($filter==='bots' && !$bot)||($filter==='others' && $bot))continue;
            $status=(int)($r['status']??0);
            $kind=(string)($r['kind']??'other');
            $path=monitor_safe_path((string)($r['path']??''));
            $agent=(string)($r['agent']??'unknown');
            $source=monitor_source($path); // Recalculate, never trust old or imported log categories.
            ++$counts['requests'];
            if ($status>=200 && $status<300)++$counts['success_2xx'];
            elseif($status>=300 && $status<400)++$counts['redirect_3xx'];
            elseif($status>=400 && $status<500)++$counts['errors_4xx'];
            elseif($status>=500)++$counts['errors_5xx'];
            if ($status===304)++$counts['not_modified_304'];
            $byAgent[$agent]=($byAgent[$agent]??0)+1;
            $byKind[$kind]=($byKind[$kind]??0)+1;
            $bySource[$source]=($bySource[$source]??0)+1;
            $byDay[$day]++;
            if ($status===200 && $source==='research' && $kind==='research-section')++$counts['successful_research_sections'];
            $slug=(string)($r['book']??'');
            $book=$knownBooks[$slug]??null;
            if ($source==='books' && $book!==null) {
                $byBook[$slug]=($byBook[$slug]??0)+1;
                if($status===200 && in_array($kind,['print-page','json-print-page','page-spread'],true)) {
                    $first=(int)($r['from']??0); $last=(int)($r['to']??$first);
                    if ($first>0 && $last>=$first && $last<=$first+1 && $last<=(int)$book['page_count']) {
                        ++$counts['successful_book_pages'];
                        for($pn=$first;$pn<=$last;$pn++){ $unique[$slug.':'.$pn]=true; $bookUnique[$slug][$pn]=true; }
                    }
                }
            }
        }
        fclose($fh);
    }
    $counts['distinct_book_pages']=count($unique);
    arsort($byAgent);arsort($byKind);arsort($bySource);
    $books=[];
    foreach(all_books() as $b) $books[]=['slug'=>$b['slug'],'title'=>$b['title'],'total_print_pages'=>(int)$b['page_count'],
        'requests'=>(int)($byBook[$b['slug']]??0),'distinct_print_pages_served'=>count($bookUnique[$b['slug']]??[])];
    return [
      'schema_version'=>'1.0','generated_at_utc'=>gmdate('Y-m-d\TH:i:s\Z'),
      'access'=>'private-authenticated','window_days'=>$days,'visitor_filter'=>$filter,
      'evidence_scope'=>'observed_http_requests_only','crawler_identity'=>'self_reported_user_agent_unverified',
      'no_claim_of'=>['verified_bot_identity','search_indexing','model_training','external_agent_comprehension'],
      'source_priority'=>'Official books are authoritative; research is supplemental and not approved Eviulon doctrine.',
      'completeness'=>['days_with_log_files'=>$logDays,'log_lines_seen'=>$linesRead,'invalid_lines'=>$invalidLines,'partial'=>$partial],
      'metrics'=>$counts,'by_source'=>$bySource,'by_claimed_agent'=>$byAgent,'by_request_kind'=>$byKind,'by_day_utc'=>$byDay,
      'official_books'=>$books,
    ];
}
function monitor_summary_json(): never {
    monitor_require_auth();
    if (!in_array(strtoupper($_SERVER['REQUEST_METHOD']??'GET'),['GET','HEAD'],true)) {
        header('Allow: GET, HEAD');http_response_code(405);exit;
    }
    [$days,$filter]=monitor_parameters();
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(monitor_summary($days,$filter), JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_THROW_ON_ERROR);
    exit;
}
function monitor_dashboard(): never {
    monitor_require_auth();
    [$days,$filter]=monitor_parameters();
    $stats=monitor_summary($days,$filter);
    $count=$stats['metrics'];
    $desc='Private PHP request observations. User-agent names are unverified claims; requests do not prove search indexing, AI retrieval correctness, dataset inclusion, or model training.';
    render_head('Private crawler activity — Eviulon',$desc,'/admin/crawlers/',[],'noindex,nofollow,noarchive');
    echo '<main id="content" class="shell monitor-page"><p class="eyebrow">PRIVATE · OBSERVABILITY · UTC</p><h1>Crawler &amp; reading activity</h1><p class="monitor-intro">'.h($desc).' <strong>Official books remain authoritative.</strong> Research is supplemental. <a href="/admin/crawlers/summary.json?days='.$days.'&amp;filter='.h($filter).'">Download authenticated aggregate JSON</a>.</p>';
    echo '<form class="monitor-filters" method="get" action="/admin/crawlers/"><label>Window <select name="days">';
    foreach([7,30,90] as $d)echo '<option value="'.$d.'"'.($d===$days?' selected':'').'>'.$d.' days</option>';
    echo '</select></label><label>Visitor type <select name="filter">';
    foreach(['bots'=>'Claimed crawlers','all'=>'All requests','others'=>'Other visitors'] as $v=>$title)echo '<option value="'.h($v).'"'.($v===$filter?' selected':'').'>'.h($title).'</option>';
    echo '</select></label><button class="btn btn-primary" type="submit">Apply</button></form>';
    echo '<div class="monitor-metrics">';
    foreach(['Observed requests'=>'requests','HTTP 2xx'=>'success_2xx','HTTP 4xx'=>'errors_4xx','Distinct official print pages served'=>'distinct_book_pages'] as $label=>$key)echo '<div><strong>'.number_format($count[$key]).'</strong><span>'.h($label).'</span></div>';
    echo '</div>';
    if (!is_dir(monitor_log_dir()) || !is_writable(monitor_log_dir()))echo '<p class="monitor-warning">Monitoring logs are not writable; coverage may be incomplete.</p>';
    if ($stats['completeness']['partial'])echo '<p class="monitor-warning"><strong>Partial data:</strong> the log scan reached a resource limit. Do not interpret totals as exhaustive.</p>';
    if ($count['requests']===0)echo '<p class="monitor-warning">No matching PHP requests observed. This does not mean the library is unindexed.</p>';
    echo '<div class="monitor-columns"><section><h2>Official books vs supplemental research</h2><table><thead><tr><th>Source</th><th>Observed requests</th></tr></thead><tbody>';
    $labels=['books'=>'Books — official','research'=>'Research — supplemental','unattributed-search-or-agent'=>'Search / AG-UI — source not attributable','site-or-service'=>'Site and service'];
    foreach($labels as $key=>$label)echo '<tr><td>'.h($label).'</td><td>'.number_format($stats['by_source'][$key]??0).'</td></tr>';
    echo '</tbody></table><p>Mixed search and AG-UI traffic is intentionally not assigned to a book or report without reliable per-tool provenance.</p></section>';
    echo '<section><h2>Claimed crawler category</h2><table><thead><tr><th>Self-reported identity</th><th>Requests</th></tr></thead><tbody>';
    foreach($stats['by_claimed_agent'] as $name=>$value)echo '<tr><td>'.h($name).'</td><td>'.number_format($value).'</td></tr>';
    echo '</tbody></table></section></div>';
    echo '<section><h2>Official-book page request coverage</h2><p>Counts reflect HTTP 200 deliveries, not verified indexing. One landscape spread can count for two print pages.</p><div class="monitor-table-scroll"><table><thead><tr><th>Book</th><th>Requests</th><th>Unique pages served</th><th>Total pages</th></tr></thead><tbody>';
    foreach($stats['official_books'] as $b)echo '<tr><td><a href="/'.h($b['slug']).'/">'.h($b['title']).'</a></td><td>'.$b['requests'].'</td><td>'.$b['distinct_print_pages_served'].'</td><td>'.$b['total_print_pages'].'</td></tr>';
    echo '</tbody></table></div></section>';
    echo '<div class="monitor-columns"><section><h2>Resource types</h2><table><thead><tr><th>Kind</th><th>Requests</th></tr></thead><tbody>';
    foreach($stats['by_request_kind'] as $name=>$value)echo '<tr><td>'.h($name).'</td><td>'.number_format($value).'</td></tr>';
    echo '</tbody></table></section><section><h2>Daily requests (UTC)</h2><table><thead><tr><th>Day</th><th>Requests</th></tr></thead><tbody>';
    foreach($stats['by_day_utc'] as $day=>$value)echo '<tr><td>'.h($day).'</td><td>'.number_format($value).'</td></tr>';
    echo '</tbody></table></section></div>';
    echo '<aside class="monitor-disclaimer"><h2>Evidence boundaries</h2><p>This is an <strong>HTTP access monitor only</strong>. Logs cannot establish bot ownership, whether a third-party service indexed a page, whether an agent accurately cited it, or whether any model trained on it. Verify crawler identity using your host access logs and provider-published IP/DNS procedures; use Google Search Console, Bing Webmaster Tools, Common Crawl records, and controlled agent transcripts for later evidence levels. New records omit raw user-agent strings, referrers, cookies, IPs, search terms, and request bodies. Older on-server records may contain legacy user-agent/referrer fields; see the privacy upgrade guidance.</p><p>Request logs rotate daily with up to 90 days retention. This private summary is not indexed, cached, or exposed to the public search/API. Missing log days and scan limits are disclosed in its JSON <code>completeness</code> field.</p></aside></main>';
    render_foot();exit;
}
