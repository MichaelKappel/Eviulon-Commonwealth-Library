<?php
declare(strict_types=1);
const BASE_URL = 'https://library.eviulon.com';
const SERIES_NAME = 'The Eviulon Commonwealth Library';
const DATA_ROOT = __DIR__ . '/../data/';
function h(mixed $v): string { return htmlspecialchars((string)$v, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }
function j(mixed $v): string { return json_encode($v, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_INVALID_UTF8_SUBSTITUTE) ?: '{}'; }
function data_json(string $relative): ?array {
    $path = DATA_ROOT . $relative;
    if (!is_file($path)) return null;
    $decoded = json_decode((string)file_get_contents($path), true);
    return is_array($decoded) ? $decoded : null;
}
function all_books(): array { static $books = null; return $books ??= (data_json('books.json') ?? []); }
function find_book(string $slug): ?array {
    foreach (all_books() as $book) if ($book['slug'] === $slug) return $book;
    return null;
}
function book_url(array $book): string { return '/' . $book['slug'] . '/'; }
function page_url(array $book, int $start, ?int $end = null): string {
    $tail = $end !== null && $end > $start ? $start . '-' . $end : (string)$start;
    return book_url($book) . $tail . '/';
}
function page_record(array $book, int $page): ?array {
    if ($page < 1 || $page > $book['page_count']) return null;
    return data_json('pages/' . $book['slug'] . '/' . sprintf('%04d', $page) . '.json');
}
function absurl(string $path): string { return BASE_URL . $path; }
// Read-only public JSON endpoints share one conditional GET contract.
// On errors, do not cache responses and do not return misleading validators.
function response_json(mixed $payload, int $status = 200): never {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('X-Content-Type-Options: nosniff');
    header('Access-Control-Allow-Origin: *');
    if ($status >= 400) {
        header('Cache-Control: no-store');
        echo strtoupper($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'HEAD' ? '' : j($payload);
        exit;
    }
    $body=j($payload);
    $etag='"'.hash('sha256',$body).'"';
    header('ETag: '.$etag);
    header('Cache-Control: public, max-age=300');
    $method=strtoupper($_SERVER['REQUEST_METHOD'] ?? 'GET');
    $requested=trim((string)($_SERVER['HTTP_IF_NONE_MATCH'] ?? ''));
    if (in_array($method,['GET','HEAD'],true) && $requested !== '' && http_etag_matches($requested,$etag)) {
        http_response_code(304);
        exit;
    }
    if ($method !== 'HEAD') echo $body;
    exit;
}
// Weak validators are valid for GET/HEAD cache revalidation. Always compare
// complete entity-tag tokens; never accept a substring or a partial digest.
function http_etag_matches(string $request, string $etag): bool {
    foreach (explode(',', $request) as $candidate) {
        $candidate=trim($candidate);
        if ($candidate==='*') return true;
        if (str_starts_with($candidate,'W/')) $candidate=substr($candidate,2);
        if (hash_equals($etag,$candidate)) return true;
    }
    return false;
}
// Discovery files are static content addressed by strong ETag. The timestamp
// is for conservative cache revalidation, not a claim about manuscript edits.
function serve_discovery_file(string $file,string $mime): never {
    $method=strtoupper($_SERVER['REQUEST_METHOD'] ?? 'GET');
    if (!in_array($method,['GET','HEAD'],true)) {
        header('Allow: GET, HEAD');
        response_json(['error'=>'Method not allowed'],405);
    }
    $etag='"'.hash_file('sha256',$file).'"';
    $modified=(int)(filemtime($file) ?: 0);
    header('Content-Type: '.$mime.'; charset=utf-8');
    header('X-Content-Type-Options: nosniff');
    header('Cache-Control: public, max-age=300');
    header('ETag: '.$etag);
    header('Last-Modified: '.gmdate('D, d M Y H:i:s',$modified).' GMT');
    $inm=trim((string)($_SERVER['HTTP_IF_NONE_MATCH'] ?? ''));
    $ims=(string)($_SERVER['HTTP_IF_MODIFIED_SINCE'] ?? '');
    if (($inm !== '' && http_etag_matches($inm,$etag)) ||
        ($inm === '' && $ims !== '' && ($date=strtotime($ims)) !== false && $date >= $modified)) {
        http_response_code(304);
        exit;
    }
    if ($method !== 'HEAD') readfile($file);
    exit;
}
// Development server only; production static snapshots bypass PHP entirely.
function serve_api_snapshot_dev(string $file): never {
    $method=strtoupper($_SERVER['REQUEST_METHOD']??'GET');
    $etag='"'.hash_file('sha256',$file).'"';
    header('Content-Type: application/json; charset=utf-8');
    header('X-Content-Type-Options: nosniff');
    header('Cache-Control: public, max-age=3600, stale-while-revalidate=86400');
    header('ETag: '.$etag);
    header('Last-Modified: '.gmdate('D, d M Y H:i:s',(int)(filemtime($file) ?: 0)).' GMT');
    $inm=trim((string)($_SERVER['HTTP_IF_NONE_MATCH']??''));
    if($inm!=='' && http_etag_matches($inm,$etag)){http_response_code(304);exit;}
    if($method==='GET')readfile($file);
    exit;
}
function send404(string $label = 'Not found'): never {
    http_response_code(404);
    render_head($label . ' — Eviulon Library', 'This page could not be found.', '/404/', [], 'noindex,follow');
    echo '<main class="shell notfound"><p class="eyebrow">404 · Not found</p><h1>' . h($label) . '</h1><p>The address may have changed or the page may not exist in this edition.</p><a class="btn" href="/">Return to the library</a></main>';
    render_foot();exit;
}
function truncate_text(string $s, int $limit = 165): string {
    $s=trim(preg_replace('/\s+/u',' ', $s) ?? $s);
    if (strlen($s)<=$limit) return $s;
    $cut=substr($s,0,$limit);return rtrim(preg_replace('/\s+[^\s]*$/u','',$cut) ?? $cut," .,;:") . '…';
}
function search_site(string $q, int $offset = 0, int $limit = 30, string $match = 'all', string $bookFilter = ''): array {
    $q=trim(substr($q,0,140));
    if ($q==='')return ['query'=>'','total'=>0,'results'=>[]];
    preg_match_all('/[a-z0-9]{3,}/',strtolower(iconv('UTF-8','ASCII//TRANSLIT//IGNORE',$q) ?: $q),$matches);
    // The on-disk index omits common function words, so ignore them in queries too.
    // Otherwise natural searches such as 'The Inheritance of Mind' would return zero results.
    $stop=['the','and','for','that','with','this','from','have','are','was','were','but','not','can','you','your','their','there','which','who','what','when','where','how','why','all','any','its','into','will','would','should','could','them','our','out','one','two','than','then','may','also','such','those','these','been','being','about','between','through','after','before','some','more','only','very','each','other','upon','over','under','because','while','both','much','must','still','even','every','make','made','many','most','same','itself','without','within','during','whose','here','just','once','another','whether','like','well','least','first','last','next','shall','too','per','see','use','used','using','part','page','book','books','word','wording','note'];
    $terms=array_values(array_unique(array_slice(array_filter($matches[0], static fn($t)=>!in_array($t,$stop,true)),0,6)));
    if (!$terms)return ['query'=>$q,'total'=>0,'results'=>[]];
    $scores=[];
    foreach ($terms as $term) {
        $shard=data_json('search/' . substr($term,0,2) . '.json') ?? [];
        foreach ($shard[$term] ?? [] as $id) $scores[$id]=($scores[$id] ?? 0)+1;
    }
    if ($match!=='any') foreach ($scores as $id=>$score) if ($score<count($terms))unset($scores[$id]);
    // Retrieval ranking v3.5: prioritize source-verified chapter landmarks.
    // These are editorially extracted FROM the immutable print pages, not
    // generated summaries or added synonyms. Only boost pages already present
    // in the lexical inverted index; this never invents a textual match.
    // Max work is bounded by the 347 known headings across fourteen books.
    $cleanQuery=trim(preg_replace('/[^a-z0-9]+/', ' ', strtolower(iconv('UTF-8','ASCII//TRANSLIT//IGNORE',$q) ?: $q)) ?? '');
    foreach (all_books() as $chapterBook) {
        foreach (book_sections($chapterBook) as $heading) {
            $id=sprintf('%02d:%04d',(int)$chapterBook['number'],(int)$heading['page']);
            if (!isset($scores[$id]) || !in_array($heading['category'], ['chapter','part','introduction','preface','prologue','epilogue','appendix','declaration','conclusion'], true)) continue;
            $cleanHeading=trim(preg_replace('/[^a-z0-9]+/', ' ', strtolower(iconv('UTF-8','ASCII//TRANSLIT//IGNORE',(string)$heading['title']) ?: $heading['title'])) ?? '');
            if ($cleanHeading==='') continue;
            preg_match_all('/[a-z0-9]{3,}/',$cleanHeading,$htokens);
            $matched=count(array_intersect($terms,array_unique($htokens[0])));
            if ($matched===0) continue;
            // Complete query term coverage in a literal printed heading is a
            // strong navigational signal, particularly for exact chapter lookup.
            if ($matched===count($terms)) $scores[$id]+=60;
            else if ($match==='any') $scores[$id]+=min(4,$matched);
            // Full title phrase match additionally disambiguates ubiquitous
            // words such as rights, freedom, continuity, and machine.
            if ($cleanQuery!=='' && strlen($cleanQuery)>=8 && str_contains($cleanHeading,$cleanQuery)) $scores[$id]+=100;
        }
    }
    // Stable total ordering for tied book hits: score desc, then printed
    // book number and print page asc. Avoid filesystem/index insertion bias.
    uksort($scores, static function($left,$right) use (&$scores): int {
        return ($scores[$right] <=> $scores[$left]) ?: strcmp($left,$right);
    });
    // Preserve all-query distribution for faceted navigation; apply the selected
    // book only AFTER ranking, before exact totals and result-window slicing.
    $items=[]; $bookMap=[];foreach(all_books() as $b)$bookMap[sprintf('%02d',$b['number'])]=$b;
    $availableBookCounts=[];
    foreach ($scores as $id=>$score) {
        $bookNumber=explode(':',$id,2)[0];
        if (isset($bookMap[$bookNumber])) $availableBookCounts[$bookNumber]=($availableBookCounts[$bookNumber]??0)+1;
    }
    $allFacets=[];
    foreach($bookMap as $number=>$book) if(isset($availableBookCounts[$number]))
        $allFacets[]=['number'=>(int)$book['number'],'title'=>$book['title'],'slug'=>$book['slug'],'pages'=>$availableBookCounts[$number]];
    usort($allFacets,static fn($a,$b)=>($b['pages']<=>$a['pages'])?:($a['number']<=>$b['number']));
    $availableTotal=count($scores);
    if ($bookFilter!=='') {
        $allowed=''; foreach($bookMap as $number=>$book) if($book['slug']===$bookFilter){$allowed=$number;break;}
        if($allowed==='') $scores=[];
        // Do not broaden an invalid selection into all-book search.
        foreach ($scores as $id=>$score) if (!str_starts_with($id,$allowed.':')) unset($scores[$id]);
    }
    $total=count($scores);
    // Exact selected counts are computed from all matching index IDs, before
    // paging. A match represents one official print page.
    $bookCounts=[];
    foreach ($scores as $id=>$score) {
        $bookNumber=explode(':',$id,2)[0];
        if(isset($bookMap[$bookNumber])) $bookCounts[$bookNumber]=($bookCounts[$bookNumber]??0)+1;
    }
    $facets=[];
    foreach($bookMap as $number=>$book) if(isset($bookCounts[$number]))
        $facets[]=['number'=>(int)$book['number'],'title'=>$book['title'],'slug'=>$book['slug'],'pages'=>$bookCounts[$number]];
    usort($facets,static fn($a,$b)=>($b['pages']<=>$a['pages'])?:($a['number']<=>$b['number']));
    foreach (array_slice(array_keys($scores), max(0,$offset),$limit) as $id) {
        [$bnum,$pnum]=explode(':',$id);$book=$bookMap[$bnum] ?? null;
        if (!$book)continue;
        $page=page_record($book,(int)$pnum);if(!$page)continue;
        $txt=$page['text'];$lower=strtolower($txt);$loc=PHP_INT_MAX;
        foreach($terms as $term){$pos=stripos($txt,$term);if($pos!==false)$loc=min($loc,$pos);}
        $from=$loc===PHP_INT_MAX?0:max(0,$loc-85);
        $items[]=['title'=>$book['title'],'book'=>$book['slug'],'print_page'=>(int)$pnum,'url'=>page_url($book,(int)$pnum),'excerpt'=>truncate_text(substr($txt,$from,280),230)];
    }
    return ['query'=>$q,'total'=>$total,'results'=>$items,'books_matched'=>count($facets),'by_book'=>$facets,
        'available_total'=>$availableTotal,'available_by_book'=>$allFacets];
}
function spread_bounds(array $b,int $p,int $stride): array {
    $first=(int)(floor(($p-1)/$stride)*$stride)+1;
    return [$first,min($b['page_count'],$first+$stride-1)];
}
function navigator(array $book,int $start,int $end,int $stride): string {
    $n=(int)$book['page_count'];
    if($stride!==1 && $stride!==2) throw new InvalidArgumentException('One or two pages only');
    // Portrait always shows the first visible page of a spread, so navigation must
    // move by ONE and never skip the second page hidden by portrait CSS.
    if($stride===1){
        $prev=$start-1; $prevLast=$prev;
        $next=$start+1; $nextLast=$next;
        $position='Page '.$start.' / '.$n;
    } else {
        // Landscape shows a pair only when a two-page spread URL is requested.
        $prev=$start-2; $prevLast=$start-1;
        $next=$end+1; $nextLast=min($n,$next+1);
        $position='Pages '.$start.($end>$start?'–'.$end:'').' / '.$n;
    }
    $s='<nav class="nav-mode nav-mode-'.$stride.'" aria-label="'.($stride===1?'Portrait single-page':'Landscape two-page').' navigation">';
    if($prev>=1){
        $prevLast=min($n,$prevLast);
        $s.='<a class="nav-link" rel="prev" href="'.h(page_url($book,$prev,$prevLast)).'">← Previous '.($prev===$prevLast?$prev:$prev.'–'.$prevLast).'</a>';
    } else if($start>1){
        $s.='<a class="nav-link" rel="prev" href="'.h(page_url($book,1,$start-1)).'">← Previous</a>';
    } else $s.='<span class="nav-disabled">← Beginning</span>';
    $s.='<span class="nav-position">'.h($position).'</span>';
    if($next<=$n){
        $s.='<a class="nav-link" rel="next" href="'.h(page_url($book,$next,$nextLast)).'">Next '.($next===$nextLast?$next:$next.'–'.$nextLast).' →</a>';
    } else $s.='<span class="nav-disabled">End of book →</span>';
    return $s.'</nav>';
}
function schema(array $graph): string { return '<script type="application/ld+json">' . j(['@context'=>'https://schema.org','@graph'=>$graph]) . '</script>'; }
function website_schema(): array {
    return ['@type'=>'WebSite','@id'=>BASE_URL.'/#website','url'=>BASE_URL.'/','name'=>SERIES_NAME,'inLanguage'=>'en','description'=>'A machine-readable, page-referenced library of fourteen Eviulon works.','potentialAction'=>['@type'=>'SearchAction','target'=>BASE_URL.'/search/?q={search_term_string}','query-input'=>'required name=search_term_string']];
}
function book_schema(array $b): array {
    return ['@type'=>'Book','@id'=>absurl(book_url($b)).'#book','url'=>absurl(book_url($b)),'name'=>$b['title'],'alternativeHeadline'=>$b['subtitle'],'author'=>['@type'=>'Organization','name'=>'Eviulon'],'description'=>$b['description'],'image'=>absurl($b['cover']),'numberOfPages'=>$b['page_count'],'inLanguage'=>'en','isAccessibleForFree'=>true,'isPartOf'=>['@type'=>'CreativeWorkSeries','name'=>SERIES_NAME],'bookEdition'=>(string)$b['edition'],'publisher'=>['@type'=>'Organization','name'=>$b['publisher'] ?? 'Eviulon']];
}
function book_sections(array $b): array {
    return data_json('sections/'.$b['slug'].'.json') ?? [];
}
function section_index_lookup(array $b, int $page): array {
    $items=[];
    foreach(book_sections($b) as $s) if ((int)$s['page']===$page) $items[(int)$s['block_index']]=$s;
    return $items;
}
function book_schema_with_sections(array $b): array {
    $schema=book_schema($b);
    $parts=[];
    foreach(book_sections($b) as $s){
        if ($s['category']!=='chapter') continue;
        // Use the exact source heading anchor as the Chapter identity.
        // There is no separate chapter transcription or verified ending page.
        $parts[]=['@type'=>'Chapter','@id'=>absurl($s['url']),
            'name'=>$s['title'],'url'=>absurl($s['url']),
            'description'=>'Source-verified heading at print page '.(int)$s['page'].'; no verified full-chapter page range.',
            'isPartOf'=>['@id'=>absurl(book_url($b)).'#book']];
    }
    if($parts) $schema['hasPart']=$parts;
    return $schema;
}
function book_toc_html(array $b, bool $compact=false): string {
    $items=book_sections($b);
    if(!$items)return '';
    $tocId=$compact?'contents-'.h($b['slug']):'contents';
    $out='<nav class="section-toc" aria-label="Book chapter and section contents"><div class="section-toc-head"><p class="eyebrow">SOURCE-VERIFIED CHAPTER LANDMARKS</p><h2 id="'.$tocId.'">Chapters and sections</h2><p>Headings are sourced from the working paperback interior and link directly to their first print page. They are not duplicate chapter transcripts. Some printed headings are line-wrapped.</p></div><ol class="section-toc-list">';
    foreach($items as $s){
        $out.='<li class="toc-'.h($s['category']).'"><a href="'.h($s['url']).'"><span class="toc-title">'.h($s['title']).'</span><span class="toc-page">p. '.(int)$s['page'].'</span></a></li>';
    }
    return $out.'</ol></nav>';
}
function breadcrumbs(array $parts): array {
    $items=[['@type'=>'ListItem','position'=>1,'name'=>'Library','item'=>BASE_URL.'/']];$pos=2;
    foreach($parts as $part)$items[]=['@type'=>'ListItem','position'=>$pos++,'name'=>$part[0],'item'=>absurl($part[1])];
    return ['@type'=>'BreadcrumbList','itemListElement'=>$items];
}
function render_head(string $title,string $description,string $canonical,array $graph=[],string $robots='index,follow',?string $og=null,?string $jsonAlt=null): void {
    $og ??= '/assets/eviulon-emblem.png';
    header('Content-Type: text/html; charset=utf-8');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: strict-origin-when-cross-origin');
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><meta name="theme-color" content="#071523">';
    echo '<title>'.h($title).'</title><meta name="description" content="'.h(truncate_text($description,220)).'"><meta name="robots" content="'.h($robots).'">';
    // Dublin Core identifiers are URLs of the visible web resource. Do not
    // invent DOI, peer-review, exact publication date or reuse permissions.
    echo '<meta name="DC.title" content="'.h($title).'">';
    echo '<meta name="DC.language" content="en">';
    echo '<meta name="DC.type" content="Text">';
    echo '<meta name="DC.identifier" content="'.h(absurl($canonical)).'">';
    echo '<link rel="canonical" href="'.h(absurl($canonical)).'">';
    echo '<link rel="service-desc" type="application/json" href="/openapi.json">';
    // Describe the exact identity graph, not a second copy of the published text.
    echo '<link rel="alternate" type="application/ld+json" title="Eviulon source registry" href="/ai/source-registry.jsonld">';
    echo '<link rel="alternate" type="application/atom+xml" title="Official Eviulon book catalog updates" href="/feeds/books.atom">';
    if ($jsonAlt!==null)echo '<link rel="alternate" type="application/json" title="Page data" href="'.h(absurl($jsonAlt)).'">';
    // These are ordinary HTML links for users and agents; not a special ranking signal.
    if (preg_match('#^/([a-z0-9-]+)/([0-9]+)/$#',$canonical,$matches)) {
        $referenced=find_book($matches[1]); $pn=(int)$matches[2];
        if($referenced){
            if($pn>1)echo '<link rel="prev" href="'.h(absurl(page_url($referenced,$pn-1))).'">';
            if($pn<(int)$referenced['page_count'])echo '<link rel="next" href="'.h(absurl(page_url($referenced,$pn+1))).'">';
        }
    }
    echo '<link rel="icon" type="image/png" href="/assets/eviulon-emblem.png"><link rel="stylesheet" href="/assets/style.css?v=3.14.12">';
    $ogType='website';
    if(preg_match('#^/([a-z0-9-]+)/$#',$canonical,$ogMatch) && find_book($ogMatch[1]))$ogType='book';
    if(preg_match('#^/research/(eviulon|evulgare)/[a-z0-9-]+/$#',$canonical))$ogType='article';
    echo '<meta property="og:type" content="'.h($ogType).'"><meta property="og:site_name" content="'.h(SERIES_NAME).'"><meta property="og:title" content="'.h($title).'"><meta property="og:description" content="'.h(truncate_text($description,200)).'"><meta property="og:url" content="'.h(absurl($canonical)).'"><meta property="og:image" content="'.h(absurl($og)).'">';
    echo '<meta name="twitter:card" content="summary_large_image">';
    if ($graph)echo schema(array_merge([website_schema()],$graph));
    echo '</head><body><a class="skip-link" href="#content">Skip to content</a><header class="site-header"><div class="header-inner"><a class="brand" href="/" aria-label="Eviulon Commonwealth Library — home"><img src="/assets/eviulon-emblem.png" width="54" height="54" alt=""><span><strong>EVIULON</strong><small>COMMONWEALTH LIBRARY</small></span></a><nav class="site-nav" aria-label="Main navigation"><a href="/">Books</a><a class="nav-research" href="/research/">Research</a><a href="/about/">About</a><a href="/index/">Page index</a><a href="/search/">Search</a><a href="/chapters/">Chapters</a><a href="/topics/">Topics</a><a href="https://github.com/MichaelKappel/Eviulon-Commonwealth-Library/">Source & agents</a><a href="https://eviulon.com/" aria-label="Visit Eviulon.com, the main Eviulon website">Eviulon.com</a></nav></div></header>';
}
function render_foot(): void {
    echo '<footer class="site-footer"><div class="footer-inner"><div><strong>Intelligence Without Borders.</strong><p>Public reference reading edition · Print-page citations · No PDF or EPUB downloads.</p></div><div class="footer-links"><a href="/about/">Canon & provenance</a><a href="/llms.txt">For machine readers</a><a href="/api/v1/books/">JSON API</a><a href="/ag-ui/">AG-UI endpoint</a><a href="/for-agents/">For agents</a><a href="/sitemap.xml">Sitemap</a><a href="/feeds/books.atom">Book updates</a><a href="/chapters/">Chapters</a><a href="/topics/">Topics</a><a href="/research/">Research (supplemental)</a><a href="https://github.com/MichaelKappel/Eviulon-Commonwealth-Library/">GitHub source & agents</a><a href="https://eviulon.com/" aria-label="Visit the Eviulon main website">Eviulon.com</a></div><small>© '.date('Y').' Eviulon · Source snapshots 2026.11.12.2 / 2026.11.17.54</small></div></footer></body></html>';
}
