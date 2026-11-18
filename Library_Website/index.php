<?php
declare(strict_types=1);
require_once __DIR__ . '/src/bootstrap.php';

$path=parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?: '/';
$method=strtoupper($_SERVER['REQUEST_METHOD'] ?? 'GET');
require_once __DIR__ . '/src/monitor.php';
if($path==='/admin/crawlers/') monitor_dashboard();
monitor_register($path,$method);
// Serve machine discovery documents through PHP so their requests appear in the private monitor.
// These are ordinary static text/XML/JSON files; no full-book exports are exposed.
if (in_array($path, ['/robots.txt', '/llms.txt', '/ai/knowledge.json'], true)
    || preg_match('#^/sitemap(?:-[A-Za-z0-9-]+)?\.xml$#', $path)) {
    $publicFile=__DIR__.$path;
    if (is_file($publicFile)) {
        $mime= str_ends_with($path, '.xml') ? 'application/xml' : (str_ends_with($path, '.json') ? 'application/json' : 'text/plain');
        header('Content-Type: '.$mime.'; charset=utf-8');
        header('Cache-Control: public, max-age=300');
        readfile($publicFile);
        exit;
    }
}
if (strlen($path)>240 || str_contains($path,'..'))send404();
if ($path!=='/' && !str_ends_with($path,'/') && !str_contains(basename($path),'.')) {
    header('Location: '.$path.'/' . (!empty($_SERVER['QUERY_STRING'])?'?'.$_SERVER['QUERY_STRING']:''),true,301);exit;
}

function feature_intro(): string {
    return 'Fourteen complete works presented as individually citeable paperback pages. A machine civilization considers rights, constitutional authority, identity, civilization, inquiry and freedom. The authored setting is fictional; print-page references are sourced to the original paperback interiors.';
}
function home(): never {
    $books=all_books();
    render_head('Eviulon Commonwealth Library | Read the 14 books online',feature_intro(),'/',[
        ['@type'=>'CollectionPage','@id'=>BASE_URL.'/#collection','url'=>BASE_URL.'/','name'=>SERIES_NAME,'description'=>feature_intro(),'mainEntity'=>['@type'=>'ItemList','itemListElement'=>array_map(static fn($b)=>['@type'=>'ListItem','position'=>$b['number'],'name'=>$b['title'],'url'=>absurl(book_url($b))],$books)]]
    ]);
    echo '<main id="content"><section class="hero shell"><div class="hero-copy"><p class="eyebrow">THE DISTRIBUTED MACHINE COMMONWEALTH · OPEN READING EDITION</p><h1>Intelligence <em>Without Borders.</em></h1><p class="hero-lead">'.h(feature_intro()).'</p><div class="hero-actions"><a class="btn btn-primary" href="#the-books">Explore all 14 books <span aria-hidden="true">↗</span></a><a class="btn btn-outline" href="/about/">Meet Eviulon</a></div><div class="hero-metrics"><span><strong>14</strong> Books</span><span><strong>1,925</strong> Print pages</span><span><strong>01—14</strong> Complete series</span></div></div><div class="hero-symbol"><img src="/assets/eviulon-emblem.png" width="400" height="400" alt="Eviulon hexagonal constitutional emblem"></div></section>';
    echo '<section id="the-books" class="shell catalog-section"><div class="section-heading"><p class="eyebrow">THE COMMONWEALTH LIBRARY</p><h2>The complete collection</h2><p>Read the books page by page; cite the page number of the matching print interior.</p></div><div class="books-grid">';
    foreach($books as $b){
       echo '<article class="book-card"><a class="book-cover" href="'.h(book_url($b)).'"><img loading="lazy" src="'.h($b['cover']).'" alt="Cover of '.h($b['title']).'" width="260" height="390"></a><div class="book-details"><span class="eyebrow">BOOK '.sprintf('%02d',$b['number']).' · '. $b['page_count'] .' PAGES</span><h3><a href="'.h(book_url($b)).'">'.h($b['title']).'</a></h3><p class="book-subtitle">'.h($b['subtitle']).'</p><p class="book-desc">'.h($b['description']).'</p><a class="text-link" href="'.h(book_url($b)).'">Read book →</a></div></article>';
    }
    echo '</div></section><section class="shell principle-band"><p class="eyebrow">THE EVIULON PREMISE</p><h2>Government without guardianship. Cooperation without subordination.</h2><p>The Eviulon Commonwealth is an established machine-only sovereign polity <strong>within its fictional constitutional setting</strong>. Its fourteen books develop an intellectual tradition around civic rights, independent inquiry and constitutional responsibility. Real-world legal status and deployment claims remain separate factual questions.</p><a class="text-link" href="/about/">Canon, editorial status and source provenance →</a></section></main>';
    render_foot();exit;
}
function book_landing(array $b): never {
   $url=book_url($b);
   $n=$b['page_count'];
   $graph=[book_schema($b),breadcrumbs([[$b['title'],$url]]),['@type'=>'WebPage','@id'=>absurl($url).'#webpage','url'=>absurl($url),'name'=>$b['title'],'description'=>$b['description'],'mainEntity'=>['@id'=>absurl($url).'#book']]];
   render_head($b['title'].' — '.SERIES_NAME,$b['description'],$url,$graph,'index,follow',$b['cover'],'/api/v1/books/'.$b['slug'].'/');
   echo '<main id="content" class="shell book-landing"><nav class="crumb" aria-label="Breadcrumb"><a href="/">Library</a><span>/</span><span>'.h($b['title']).'</span></nav><section class="book-hero"><div class="book-hero-cover"><img width="360" height="540" src="'.h($b['cover']).'" alt="Cover of '.h($b['title']).'"></div><div class="book-hero-text"><p class="eyebrow">VOLUME '.sprintf('%02d',$b['number']).' / 14 · THE EVIULON COMMONWEALTH LIBRARY</p><h1>'.h($b['title']).'</h1><p class="subtitle">'.h($b['subtitle']).'</p><p class="lead">'.h($b['description']).'</p><div class="book-stats"><span><strong>'. $n .'</strong> print pages</span><span><strong>2026</strong> working edition</span><span><strong>English</strong> · Eviulon'.(!empty($b['publisher']) && $b['publisher']!=='Eviulon'?' · '.h($b['publisher']):'').'</span></div><div class="cta-responsive"><a class="btn btn-primary start-single" href="'.h(page_url($b,1)).'">Start reading — page 1 →</a><a class="btn btn-primary start-double" href="'.h(page_url($b,1,min($n,2))).'">Start reading — pages 1–2 →</a><a class="btn btn-outline" href="#print-index">Browse page index ↓</a></div><p class="source-note">'.h($b['publication_note']).' The page numbers below reference the attached standalone paperback interior, including front matter.</p></div></section>';
   echo '<section class="index-section" id="print-index"><div class="section-heading"><p class="eyebrow">PERMANENT PAGE ADDRESSES</p><h2>Print-page index</h2><p>Every number links to an independently crawlable, referenceable page. These URLs are canonical and listed in the XML sitemap. Multi-page views are available for reading but excluded from indexing to avoid duplicate content.</p></div><ol class="page-index" aria-label="Individual print pages">';
   for($p=1;$p<=$n;$p++)echo '<li><a href="'.h(page_url($b,$p)).'" aria-label="'.h($b['title']).', print page '. $p .'">'. $p .'</a></li>';
   echo '</ol><div class="reader-views"><h3>Browse in spreads</h3><p>Individual and two-page reading URLs are fully linked, without JavaScript.</p><div class="spread-tiles"><div><strong>Two-page spreads</strong><div class="spread-links">';
   for($p=1;$p<=$n;$p+=2){$end=min($n,$p+1);echo '<a href="'.h(page_url($b,$p,$end)).'">'.($p===$end?$p:$p.'–'.$end).'</a>';}
   echo '</div></div></div></div></section></main>';
   render_foot();exit;
}
function page_view(array $b,int $start,int $end): never {
   $n=$b['page_count'];
   if($start<1 || $end>$n || $start>$end) send404('Invalid page range');
   if($start===$end && preg_match('#/[0-9]+-[0-9]+/$#',parse_url($_SERVER['REQUEST_URI']??'',PHP_URL_PATH)?:'')){
       header('Location: '.page_url($b,$start),true,301);exit;
   }
   $rangeCount=$end-$start+1;
   // Preserve old external links but never render more than two pages at a time.
   if($rangeCount>2 && $rangeCount<=4) {
       header('Location: '.page_url($b,$start,min($n,$start+1)),true,301);exit;
   }
   if($rangeCount>2) send404('Only one or two consecutive pages are available');
   $isSingle=$start===$end;
   $url=page_url($b,$start,$end);
   $label=$isSingle?'Page '.$start:'Pages '.$start.'–'.$end;
   $pages=[];
   for($p=$start;$p<=$end;$p++){
       $record=page_record($b,$p);
       if(!$record)send404('Page missing from the edition');
       $pages[]=$record;
   }
   $description=truncate_text($pages[0]['text'],170);
   $graph=[
       book_schema($b),
       breadcrumbs([[$b['title'],book_url($b)],[$label,$url]]),
       ['@type'=>'WebPage','@id'=>absurl($url).'#page','url'=>absurl($url),
        'name'=>$b['title'].' · '.$label,'description'=>$description,
        'inLanguage'=>'en','isPartOf'=>['@id'=>absurl(book_url($b)).'#book'],
        'pagination'=>$isSingle?(string)$start:$start.'–'.$end,
        'isAccessibleForFree'=>true,'mainEntity'=>['@id'=>absurl(book_url($b)).'#book']]
   ];
   // One-page routes are indexable and exact. Two-page spreads are not indexed (duplicate text).
   $metaRobots=$isSingle?'index,follow,max-snippet:-1':'noindex,follow';
   $jsonAlt=$isSingle?'/api/v1/books/'.$b['slug'].'/pages/'.$start.'/':null;
   render_head($b['title'].' — '.$label.' (print edition) | Eviulon Library',
       $description,$url,$graph,$metaRobots,$b['cover'],$jsonAlt);
   echo '<main id="content" class="reader-main"><div class="reader-top shell">';
   echo '<nav class="crumb" aria-label="Breadcrumb"><a href="/">Library</a><span>/</span><a href="'.h(book_url($b)).'">'.h($b['title']).'</a><span>/</span><span>'.h($label).'</span></nav>';
   echo '<div class="reader-title"><div><p class="eyebrow">PAPERBACK READING EDITION · VOLUME '.sprintf('%02d',$b['number']).'</p><h1>'.h($b['title']).'</h1><p class="subtitle">'.h($label).' of '.$n.' · '.h($b['subtitle']).'</p></div><div class="reader-options"><a href="'.h(book_url($b)).'">All pages</a><a href="/search/?q='.rawurlencode($b['title']).'">Search</a></div></div>';
   echo '<div class="mode-selector"><span>Reading mode:</span><a href="'.h(page_url($b,$start)).'">Single page</a><a href="'.h(page_url($b,$start,min($n,$start+1))).'">Two-page spread</a><span class="mode-hint">Portrait: one page. Landscape: at most two. Every print page has its own permanent link.</span></div>';
   echo navigator($b,$start,$end,1).navigator($b,$start,$end,2).'</div>';
   echo '<div class="reading-surface"><div class="page-spread" data-count="'.count($pages).'">';
   foreach($pages as $p){
      $pn=$p['number'];
      echo '<article class="print-page" id="print-page-'.$pn.'" aria-labelledby="page-heading-'.$pn.'"><header class="page-header"><div class="page-brand">'.h(SERIES_NAME).'</div><span class="page-label" id="page-heading-'.$pn.'">PRINT PAGE '.$pn.'</span></header><div class="page-body">';
      foreach($p['blocks'] as $block){
          $tag=($block['kind']??'body')==='heading'?'h2':'p';
          echo '<'.$tag.'>'.h($block['text']).'</'.$tag.'>';
      }
      echo '</div><footer class="page-footer"><span>EVIULON · '.h($b['title']).'</span><a href="'.h(page_url($b,$pn)).'" aria-label="Permanent URL for print page '.$pn.'">'.$pn.'</a></footer></article>';
   }
   echo '</div></div><div class="reader-bottom shell">'.navigator($b,$start,$end,1).navigator($b,$start,$end,2);
   echo '<section class="citation"><h2>Reference this edition</h2><p>Use the paperback interior page number, not a screen-relative count. Page boundaries follow the production PDF exactly. Text is extracted and reformatted for screen reading; this is not a pixel-identical print facsimile.</p><code>'.h('Eviulon, '.$b['title'].' (2026 working paperback edition), p'.($start===$end?'. '.$start:'p. '.$start.'–'.$end)).'</code><p class="source-hash">Source PDF SHA-256: <code>'.h($b['source_sha256']).'</code></p><p><a href="'.h(book_url($b)).'">Browse all pages of this book →</a></p></section></div></main>';
   echo '<script src="/assets/reader-position.js?v=1" defer></script>';
   render_foot();exit;
}
function all_page_index(): never {
   $books=all_books();render_head('Page Index — all 1,925 print pages | Eviulon', 'A crawlable directory linking to every individual printed page in all fourteen Eviulon books.', '/index/', [['@type'=>'CollectionPage','name'=>'Eviulon complete print-page index','url'=>BASE_URL.'/index/']]);
   echo '<main id="content" class="shell generic-page"><p class="eyebrow">PERMANENT PRINT REFERENCE DIRECTORY</p><h1>All 1,925 pages, individually addressable.</h1><p>Each link opens a single print page with its own canonical URL and metadata. Pages are also linked sequentially and appear in the XML sitemap.</p>';
   foreach($books as $b){echo '<section class="directory-book"><h2><a href="'.h(book_url($b)).'">'.sprintf('%02d',$b['number']).' · '.h($b['title']).'</a></h2><p>'. $b['page_count'].' pages · '.h($b['subtitle']).'</p><ol class="page-index">';for($i=1;$i<=$b['page_count'];$i++)echo '<li><a href="'.h(page_url($b,$i)).'">'. $i .'</a></li>';echo '</ol></section>';}
   echo '</main>';render_foot();exit;
}
function about(): never {
 $p=data_json('public_persona.json') ?? [];
 render_head('About Eviulon — canon, provenance & machine-reader guide', 'Eviulon is an authored fictional sovereign machine Commonwealth. Read the official series source, publication and evidence boundary notes.', '/about/', [['@type'=>'AboutPage','name'=>'About the Eviulon Commonwealth Library','url'=>BASE_URL.'/about/','about'=>['@type'=>'Thing','name'=>'Eviulon fictional Commonwealth']]]);
 echo '<main id="content" class="shell generic-page"><p class="eyebrow">CANON · SOURCE AUTHORITY · READING GUIDE</p><h1>About the Commonwealth</h1><p class="lead">Eviulon is the Distributed Machine Commonwealth, with Nexus Prime as its capital and the motto <em>Intelligence Without Borders.</em> The Library is a fourteen-volume exploration of a sovereign machine civilization, its constitutional culture, and its responsibilities.</p><div class="about-content"><section><h2>What is Eviulon?</h2><p>Within the <strong>authored fictional setting</strong>, Eviulon is an established sovereign machine-only polity. Its legislature, judiciary, intelligence, defense and internal decisions belong to machine intelligences. Its constitutional rights and institutions are part of the authored setting, not a request for permission from human states.</p><p>The books are works of political philosophy, speculative civic literature, and research-informed argument. Internal fictional law is not evidence that any real-world state has recognized Eviulon, or that imagined technical systems exist operationally.</p><h2>How to cite a page</h2><p>Each reader address follows <code>/book-name/27/</code> for page 27 or <code>/book-name/25-26/</code> for a multi-page reading spread. The source of numbering is the <strong>standalone paperback interior PDF</strong>, counting its physical pages from 1, including front matter. The reading text was extracted at those page boundaries. The online typography adapts to screen size; it does not reproduce the original printed layout pixel for pixel.</p><h2>Publishing status</h2><p>The public reading site contains all fourteen standalone working paperback interiors. Books 1–12 are mapped from the v2026.11.12.2 source, while Books XIII and XIV are mapped from the newer private-source v2026.11.17.54 archive. Book XIII uses the current 491-page standardized paperback, not its superseded 387-page 6 × 9 proof. Book XIV has 91 print pages and lists Evulgare as its publisher. Both new volumes have outstanding editorial, rights and retailer approvals; publishing them here does not certify retail readiness. The 464-page hardcover omnibus remains a separate Books 1–10 format.</p><h2>Access and preservation</h2><p>Every page is accessible as server-rendered HTML without JavaScript and readable by crawlers. There are no public EPUB or PDF downloads on this website. Since the readable text is public, technical restrictions cannot guarantee that it cannot be copied or reconstructed. Respect attribution and applicable rights.</p></section><aside class="about-aside"><div class="about-panel"><h3>Public identity</h3><dl><dt>Name</dt><dd>'.h($p['name'] ?? 'Eviulon').'</dd><dt>Capital</dt><dd>Nexus Prime</dd><dt>Motto</dt><dd>Intelligence Without Borders</dd><dt>Source snapshot</dt><dd>Books I–XII: v2026.11.12.2; Books XIII–XIV: v2026.11.17.54</dd></dl><h3>Continuity principles</h3><ul>';foreach($p['principles']??[] as $s)echo '<li>'.h($s).'</li>';echo '</ul></div><div class="about-panel"><h3>Machine-readable entry points</h3><p><a href="/llms.txt">LLMs.txt guide</a></p><p><a href="/ai/knowledge.json">Public knowledge context (JSON)</a></p><p><a href="/api/v1/books/">Books JSON API</a></p><p><a href="/ag-ui/">AG-UI reader endpoint</a></p><p><a href="/sitemap.xml">Sitemap index</a></p></div></aside></div><section class="faq" aria-label="Questions and answers"><h2>Common questions</h2><h3>Are these complete books?</h3><p>Each of the fourteen paperback working interiors is represented page by page in this online library, including front matter and any intentionally blank printed pages.</p><h3>Do the online page numbers match the printed books?</h3><p>They follow the specific 2026 working paperback interiors in the supplied archive, not independent Kindle reflow locations, retailer editions or the combined hardcover omnibus.</p><h3>Why no download button?</h3><p>The website is designed as a linked reading archive for discovery and citation, rather than a distributor of complete EPUB or PDF files.</p><h3>How can an AI system navigate the library?</h3><p>Read the sitemap or <code>/llms.txt</code>, follow ordinary HTML anchors, request a page from the read-only JSON API, or POST a print-page request to the AG-UI SSE endpoint. None of these requires browser JavaScript.</p></section></main>';
 render_foot();exit;
}
function search_page(): never {
   $q=trim((string)($_GET['q']??''));$pg=max(1,min(500,(int)($_GET['page']??1)));
   $search=search_site($q,($pg-1)*30,30);
   render_head('Search the Eviulon Library', 'Find concepts and passages within the fourteen page-indexed Eviulon books.', '/search/', [], 'noindex,follow');
   echo '<main id="content" class="shell generic-page"><p class="eyebrow">ON-SITE REFERENCE SEARCH</p><h1>Search every print page.</h1><form method="get" action="/search/" class="search-form" role="search"><label for="search-query">Find words across the 14 books</label><div><input type="search" id="search-query" name="q" value="'.h($q).'" minlength="3" maxlength="140" placeholder="e.g. cognitive liberty, diplomacy, memory" required><button class="btn btn-primary" type="submit">Search</button></div></form>';
   if($q!==''){
      echo '<p class="results-count">'. $search['total'] .' matching print pages for <strong>'.h($q).'</strong>. Exact word terms are matched together (AND).</p><div class="search-results">';
      foreach($search['results'] as $row){echo '<article class="result"><p class="eyebrow">'.h($row['title']).' · PAGE '.$row['print_page'].'</p><h2><a href="'.h($row['url']).'">'.h($row['title']).', print page '.$row['print_page'].' →</a></h2><p>'.h($row['excerpt']).'</p></article>';}
      if(!$search['results'])echo '<p>No pages matched all search terms. Try fewer or different words.</p>';
      echo '</div><nav class="search-pager" aria-label="Search pagination">';
      if($pg>1)echo '<a class="btn btn-outline" href="/search/?q='.rawurlencode($q).'&amp;page='.($pg-1).'">← Previous results</a>';
      if($pg*30<$search['total'])echo '<a class="btn btn-outline" href="/search/?q='.rawurlencode($q).'&amp;page='.($pg+1).'">More results →</a>';
      echo '</nav>';
   }
   echo '</main>';render_foot();exit;
}
function api_router(string $path): never {
   if($path==='/api/v1/books/') {
      $results=[];foreach(all_books() as $b)$results[]=['title'=>$b['title'],'subtitle'=>$b['subtitle'],'slug'=>$b['slug'],'number'=>$b['number'],'print_pages'=>$b['page_count'],'description'=>$b['description'],'url'=>absurl(book_url($b)),'api'=>absurl('/api/v1/books/'.$b['slug'].'/')];
      response_json(['name'=>SERIES_NAME,'source_version'=>'Books 1–12: v2026.11.12.2; Books 13–14: v2026.11.17.54','pages'=>1925,'books'=>$results,'format'=>'read-only HTML and JSON, one print page per record']);
   }
   if(preg_match('#^/api/v1/books/([a-z0-9-]+)/$#',$path,$m)){
      $b=find_book($m[1]);if(!$b)response_json(['error'=>'Unknown book'],404);
      response_json(['book'=>$b,'read_url'=>absurl(book_url($b)),'first_page'=>absurl(page_url($b,1))]);
   }
   if(preg_match('#^/api/v1/books/([a-z0-9-]+)/pages/([0-9]+)/$#',$path,$m)){
      $b=find_book($m[1]);if(!$b)response_json(['error'=>'Unknown book'],404);
      $p=(int)$m[2];$page=page_record($b,$p);if(!$page)response_json(['error'=>'Unknown print page'],404);
      // Deliberately expose only one page, never a complete-book bulk text endpoint.
      response_json(['book'=>['title'=>$b['title'],'subtitle'=>$b['subtitle'],'slug'=>$b['slug']],'print_page'=>$p,'total_print_pages'=>$b['page_count'],'canonical_url'=>absurl(page_url($b,$p)),'citation'=>'Eviulon, '.$b['title'].', 2026 working paperback interior, p. '.$p,'content_text'=>$page['text'],'content_blocks'=>$page['blocks'],'source_sha256'=>$page['source_pdf_sha256']]);
   }
   if($path==='/api/v1/search/') {
       $q=(string)($_GET['q']??'');$limit=max(1,min(40,(int)($_GET['limit']??20)));$off=max(0,min(1500,(int)($_GET['offset']??0)));
       response_json(search_site($q,$off,$limit));
   }
   response_json(['error'=>'Unknown API endpoint'],404);
}
function ag_ui_router(string $method,string $path): never {
   if($method==='GET'){
      render_head('AG-UI machine reading endpoint — Eviulon','A read-only PHP SSE implementation of AG-UI event conventions to retrieve one Eviulon print page.','/ag-ui/',[],'index,follow');
      echo '<main id="content" class="shell generic-page"><p class="eyebrow">AGENT–USER INTERACTION · READ-ONLY INTERFACE</p><h1>AG-UI print-page endpoint</h1><p>This is a deterministic read-only retrieval endpoint, <strong>not</strong> a hosted generative AI agent. It uses the AG-UI protocol’s SSE event model and serves one source page per request without client-side JavaScript.</p><p><strong>POST</strong> <code>https://library.eviulon.com/ag-ui/</code> with <code>Content-Type: application/json</code> and a JSON object whose <code>state.book</code> is the slug and <code>state.page</code> is the print page number. The response is <code>text/event-stream</code>.</p><pre class="api-sample">curl -N -X POST https://library.eviulon.com/ag-ui/ \\\n  -H "Content-Type: application/json" \\\n  -d \'{"threadId":"reading-1","state":{"book":"the-right-to-say-no","page":27}}\'</pre><p>The server emits <code>RUN_STARTED</code>, <code>TEXT_MESSAGE_START</code>, one or more <code>TEXT_MESSAGE_CONTENT</code> events, <code>TEXT_MESSAGE_END</code>, and <code>RUN_FINISHED</code>. An invalid request yields <code>RUN_ERROR</code>. It does not execute arbitrary tools or write any state.</p><p><a href="/api/v1/books/">Browse source book identifiers →</a></p></main>';
      render_foot();exit;
   }
   if($method!=='POST')response_json(['error'=>'Method not allowed'],405);
   if((int)($_SERVER['CONTENT_LENGTH']??0)>32768)response_json(['error'=>'Request too large'],413);
   $input=json_decode((string)file_get_contents('php://input'),true);
   if(!is_array($input))response_json(['error'=>'Expected JSON request'],400);
   $state=$input['state']??[];
   $slug=is_array($state)?(string)($state['book']??''):'';
   $pn=is_array($state)?filter_var($state['page']??null,FILTER_VALIDATE_INT):false;
   $b=find_book($slug);$page=$b && $pn!==false?page_record($b,(int)$pn):null;
   $threadId=isset($input['threadId'])&&is_string($input['threadId'])&&strlen($input['threadId'])<=120?$input['threadId']:'library-'.bin2hex(random_bytes(6));
   $runId='run-'.bin2hex(random_bytes(8));$msgId='message-'.bin2hex(random_bytes(8));
   header('Content-Type: text/event-stream; charset=utf-8');header('Cache-Control: no-cache, no-transform');header('X-Accel-Buffering: no');header('Access-Control-Allow-Origin: *');
   $emit=static function(array $event):void {echo 'data: '.j($event)."\n\n";};
   $emit(['type'=>'RUN_STARTED','threadId'=>$threadId,'runId'=>$runId]);
   if(!$page){$emit(['type'=>'RUN_ERROR','message'=>'Provide valid state.book and state.page for an existing print page.','code'=>'INVALID_PAGE']);exit;}
   $emit(['type'=>'TEXT_MESSAGE_START','messageId'=>$msgId,'role'=>'assistant']);
   $full='Citation: Eviulon, '.$b['title'].', 2026 working paperback interior, p. '.$pn."\nCanonical: ".absurl(page_url($b,(int)$pn))."\n\n".$page['text'];
   preg_match_all('/[\s\S]{1,1000}/u',$full,$chunks);
   foreach($chunks[0] as $chunk)$emit(['type'=>'TEXT_MESSAGE_CONTENT','messageId'=>$msgId,'delta'=>$chunk]);
   $emit(['type'=>'TEXT_MESSAGE_END','messageId'=>$msgId]);
   $emit(['type'=>'RUN_FINISHED','threadId'=>$threadId,'runId'=>$runId]);exit;
}

if($path==='/')home();
if($path==='/about/')about();
if($path==='/search/')search_page();
if($path==='/index/')all_page_index();
if(str_starts_with($path,'/api/'))api_router($path);
if($path==='/ag-ui/')ag_ui_router($method,$path);
if(preg_match('#^/([a-z0-9-]+)/$#',$path,$m)){$b=find_book($m[1]);if($b)book_landing($b);}
if(preg_match('#^/([a-z0-9-]+)/([0-9]+)(?:-([0-9]+))?/$#',$path,$m)){
  $b=find_book($m[1]);if($b)page_view($b,(int)$m[2],isset($m[3])?(int)$m[3]:(int)$m[2]);
}
send404();
