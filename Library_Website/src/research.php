<?php
require_once __DIR__ . "/research_links.php";
/** Supplemental research interface. Public reports, never official book doctrine. */
const RESEARCH_DISCLAIMER='Supplemental public-source research supplied for inquiry, not approved Eviulon doctrine. Assertions, dates, references and legal or technical conclusions may require independent verification. The fourteen books remain the official Eviulon library.';

function research_records(): array { static $cache=null; return $cache??=(data_json('research/reports.json')??[]); }
function research_find(string $group,string $slug): ?array {
    if(!in_array($group,['eviulon','evulgare'],true))return null;
    foreach(research_records() as $r) if($r['id']===$group.'/'.$slug)return $r;
    return null;
}
function research_part(array $r,int $n): ?array {
    if($n<1 || $n>(int)$r['parts'])return null;
    return data_json('research/parts/'.$r['id'].'/'.sprintf('%04d',$n).'.json');
}
function research_url(array $r,int $part=0): string {return $r['url'].($part?$part.'/':'');}
function research_scope(mixed $raw,bool $submitted=false): array {
    if(!$submitted && ($raw===null || $raw===''))return ['books'];
    $values=is_array($raw)?$raw:explode(',',(string)$raw);
    $scopes=[]; foreach($values as $v){if(is_string($v) && in_array($v,['books','research'],true) && !in_array($v,$scopes,true))$scopes[]=$v;}
    return $scopes;
}
function research_terms(string $q): array {
    preg_match_all('/[a-z0-9]{3,}/',strtolower(iconv('UTF-8','ASCII//TRANSLIT//IGNORE',$q) ?: $q),$matches);
    $stop=['the','and','for','that','with','this','from','have','are','was','were','but','not','can','you','your','their','there','which','who','what','when','where','how','why','all','any','its','into','will','would','should','could','them','our','out','one','two','than','then','may','also','such','those','these','been','being','about','between','through','after','before','some','more','only','very','each','other','upon','over','under','because','while','both','much','must','still','even','every','make','made','many','most','same','itself','without','within','during','whose','here','just','once','another','whether','like','well','least','first','last','next','shall','too','per','see','use','used','using','part','page','book','books','word','wording','note'];
    return array_values(array_unique(array_slice(array_filter($matches[0],static fn($t)=>!in_array($t,$stop,true)),0,6)));
}
function research_search(string $q,int $offset=0,int $limit=12,string $match='all',string $collectionFilter=''): array {
    $q=trim(substr($q,0,140));$limit=max(1,min(100,$limit));$offset=max(0,$offset);
    if($q==='')return ['query'=>'','total'=>0,'results'=>[]];
    $terms=research_terms($q);
    if(!$terms)return ['query'=>$q,'total'=>0,'results'=>[]];
    $scores=[];
    foreach($terms as $term){
        $shard=data_json('research/search/'.substr($term,0,2).'.json')??[];
        foreach($shard[$term]??[] as $id)$scores[$id]=($scores[$id]??0)+1;
    }
    if($match!=='any')foreach($scores as $id=>$n)if($n<count($terms))unset($scores[$id]);
    arsort($scores);
    $results=[];
    $lookup=[];foreach(research_records() as $r)$lookup[$r['id']]=$r;
    $availableCollectionCounts=['Eviulon'=>0,'Evulgare'=>0];
    foreach ($scores as $id=>$score) {
        $sep=strrpos($id,':');if($sep===false)continue;
        $record=$lookup[substr($id,0,$sep)]??null;
        if($record && isset($availableCollectionCounts[$record['group']])) $availableCollectionCounts[$record['group']]++;
    }
    $availableTotal=count($scores);
    if($collectionFilter!=='') {
        $collectionName=ucfirst($collectionFilter);
        foreach($scores as $id=>$score) {
            $sep=strrpos($id,':');$record=$sep===false?null:($lookup[substr($id,0,$sep)]??null);
            if(!$record || $record['group']!==$collectionName)unset($scores[$id]);
        }
    }
    $total=count($scores);
    // Match totals and collection facets include every matching SECTION,
    // not just the current page of results. Unique reports are counted by ID.
    $groupCounts=['Eviulon'=>0,'Evulgare'=>0];$reportCounts=[];
    foreach($scores as $id=>$score){
        $sep=strrpos($id,':');if($sep===false)continue;
        $rid=substr($id,0,$sep);$record=$lookup[$rid]??null;
        if(!$record)continue;
        $groupCounts[$record['group']]++;
        $reportCounts[$rid]=($reportCounts[$rid]??0)+1;
    }
    $topReports=[];
    foreach($reportCounts as $rid=>$matches){$r=$lookup[$rid];$topReports[]=['report_id'=>$rid,'title'=>$r['title'],'group'=>$r['group'],'sections'=>$matches,'url'=>$r['url']];}
    usort($topReports,static fn($a,$b)=>($b['sections']<=>$a['sections'])?:strcmp($a['report_id'],$b['report_id']));
    foreach(array_slice(array_keys($scores),$offset,$limit) as $id){
        $i=strrpos($id,':');if($i===false)continue;
        $rid=substr($id,0,$i);$part=(int)substr($id,$i+1);
        $r=$lookup[$rid]??null;if(!$r)continue;
        $record=research_part($r,$part);if(!$record)continue;
        $body=$record['text'];$p=PHP_INT_MAX;
        foreach($terms as $term){$j=stripos($body,$term);if($j!==false)$p=min($p,$j);}
        $excerpt=truncate_text(substr($body,$p===PHP_INT_MAX?0:max(0,$p-85),420),260);
        $results[]=['type'=>'research','authority'=>'supplemental_research_not_approved_doctrine','title'=>$r['title'],'group'=>$r['group'],
            'report_id'=>$r['id'],'section'=>$part,'sections'=>$r['parts'],'url'=>research_url($r,$part),
            'excerpt'=>$excerpt,'source_file'=>$r['source_file'],'source_sha256'=>$r['source_sha256']];
    }
    return ['query'=>$q,'total'=>$total,'results'=>$results,'disclaimer'=>RESEARCH_DISCLAIMER,
        'reports_matched'=>count($reportCounts),'by_collection'=>$groupCounts,'top_reports'=>array_slice($topReports,0,8),
        'available_total'=>$availableTotal,'available_by_collection'=>$availableCollectionCounts];
}
function library_search(string $q,array $scopes,int $page=1,int $limit=30,string $match='all'): array {
    $q=trim(substr($q,0,140));$page=max(1,min(500,$page));$limit=max(1,min(40,$limit));
    $books=in_array('books',$scopes,true);$research=in_array('research',$scopes,true);
    $bookLimit=$books&&$research?(int)ceil($limit*0.7):($books?$limit:0);
    $researchLimit=$research?($books?$limit-$bookLimit:$limit):0;
    $bk=$books?search_site($q,($page-1)*$bookLimit,$bookLimit,$match):['total'=>0,'results'=>[]];
    $rs=$research?research_search($q,($page-1)*$researchLimit,$researchLimit,$match):['total'=>0,'results'=>[]];
    $items=[];foreach($bk['results'] as $b){$b['type']='book';$b['authority']='official_eviulon_book';$items[]=$b;}
    foreach($rs['results'] as $r)$items[]=$r;
    return ['query'=>$q,'scope'=>$scopes,'match'=>$match==='any'?'any':'all','default_scope'=>'books','page'=>$page,'limit'=>$limit,
      'book_total'=>$bk['total'],'research_total'=>$rs['total'],'total'=>$bk['total']+$rs['total'],
      'book_results'=>array_values(array_filter($items,static fn($x)=>$x['type']==='book')),
      'research_results'=>array_values(array_filter($items,static fn($x)=>$x['type']==='research')),
      'results'=>$items,'research_disclaimer'=>RESEARCH_DISCLAIMER];
}
/** Only source-backed public facet choices; invalid values must never broaden a query. */
function validate_search_facets(mixed $book,mixed $collection): array {
    if(!is_string($book)||!is_string($collection))throw new InvalidArgumentException('Invalid search facet type');
    $book=trim($book);$collection=trim($collection);
    if($book!=='' && !find_book($book))throw new InvalidArgumentException('Unknown official book filter');
    if($collection!=='' && !in_array($collection,['eviulon','evulgare'],true))
        throw new InvalidArgumentException('Unknown research collection filter');
    return [$book,$collection];
}
/**
 * Independent result windows for human search and explicitly opted-in API clients.
 * Existing library_search remains unchanged for MCP/AG-UI backward compatibility.
 * Counts are exact index-match counts, NOT inferred from loaded result slices.
 */
function independent_search(string $q,array $scopes,int $booksPage=1,int $researchPage=1,int $perPage=50,string $match='all',string $bookFilter='',string $researchCollection=''): array {
    [$bookFilter,$researchCollection]=validate_search_facets($bookFilter,$researchCollection);
    $perPage=in_array($perPage,[25,50,100],true)?$perPage:50;
    $booksPage=max(1,min(1000,$booksPage));$researchPage=max(1,min(1000,$researchPage));
    $books=in_array('books',$scopes,true);$research=in_array('research',$scopes,true);
    $bk=$books?search_site($q,($booksPage-1)*$perPage,$perPage,$match,$bookFilter):['total'=>0,'results'=>[],'by_book'=>[],'books_matched'=>0];
    $rs=$research?research_search($q,($researchPage-1)*$perPage,$perPage,$match,$researchCollection):['total'=>0,'results'=>[],'by_collection'=>['Eviulon'=>0,'Evulgare'=>0],'reports_matched'=>0,'top_reports'=>[]];
    $bPages=max(1,(int)ceil($bk['total']/$perPage));$rPages=max(1,(int)ceil($rs['total']/$perPage));
    $booksPage=min($booksPage,$bPages);$researchPage=min($researchPage,$rPages);
    if($books && $bk['total'] && !$bk['results'])$bk=search_site($q,($booksPage-1)*$perPage,$perPage,$match,$bookFilter);
    if($research && $rs['total'] && !$rs['results'])$rs=research_search($q,($researchPage-1)*$perPage,$perPage,$match,$researchCollection);
    $booksList=[];foreach($bk['results'] as $hit){$hit['type']='book';$hit['authority']='official_eviulon_book';$booksList[]=$hit;}
    $researchList=$rs['results'];
    $window=static fn(int $count,int $current,int $pages)=>[
        'page'=>$current,'pages'=>$pages,'per_page'=>$perPage,
        'from'=>$count===0?0:($current-1)*$perPage+1,
        'to'=>min($count,$current*$perPage),'total'=>$count,
    ];
    return [
        'query'=>trim(substr($q,0,140)),'scope'=>$scopes,'default_scope'=>'books',
        'filters'=>['book_filter'=>$bookFilter,'research_collection'=>$researchCollection],
        'match'=>$match==='any'?'any':'all','pagination_mode'=>'independent',
        'page'=>1,'limit'=>$perPage,'per_page'=>$perPage,
        'book_total'=>$bk['total'],'research_total'=>$rs['total'],'total'=>$bk['total']+$rs['total'],
        'book_results'=>$booksList,'research_results'=>$researchList,
        'results'=>array_merge($booksList,$researchList),
        'book_pagination'=>$window($bk['total'],$booksPage,$bPages),
        'research_pagination'=>$window($rs['total'],$researchPage,$rPages),
        'breakdown'=>[
            'books_matched'=>$bk['books_matched']??0,'by_book'=>$bk['by_book']??[],
            'available_by_book'=>$bk['available_by_book']??[],'available_book_total'=>$bk['available_total']??0,
            'reports_matched'=>$rs['reports_matched']??0,
            'by_research_collection'=>$rs['by_collection']??['Eviulon'=>0,'Evulgare'=>0],
            'available_by_research_collection'=>$rs['available_by_collection']??['Eviulon'=>0,'Evulgare'=>0],
            'available_research_total'=>$rs['available_total']??0,
            'top_research_reports'=>$rs['top_reports']??[],
            'counting_unit'=>['books'=>'distinct print pages with keyword matches','research'=>'distinct research sections with keyword matches']
        ],
        'research_disclaimer'=>RESEARCH_DISCLAIMER,
    ];
}

function research_index(): never {
    $records=research_records();
    $counts=['Eviulon'=>0,'Evulgare'=>0];
    foreach($records as $report)if(isset($counts[$report['group']]))$counts[$report['group']]++;
    $total=array_sum($counts);
    $rawCat=$_GET['collection']??'';
    $cat=is_string($rawCat) ? trim($rawCat) : '';
    if(!in_array($cat,['Eviulon','Evulgare'],true))$cat='';
    // A canonical CollectionPage is truthful only when *all* 210 reports are
    // actually displayed; filtered query views omit the complete ItemList.
    $path='/research/';$graph=[breadcrumbs([['Research',$path]])];
    if($cat===''){
        $items=[];$i=0;
        foreach($records as $rec)$items[]=['@type'=>'ListItem','position'=>++$i,
            'name'=>$rec['title'],'url'=>absurl($rec['url'])];
        array_unshift($graph,['@type'=>'CollectionPage','@id'=>absurl($path).'#collection',
            'url'=>absurl($path),'name'=>'Eviulon and Evulgare supplemental research directory',
            'description'=>RESEARCH_DISCLAIMER,'inLanguage'=>'en',
            'mainEntity'=>['@type'=>'ItemList','numberOfItems'=>$total,
                'name'=>'210 supplemental research reports','itemListElement'=>$items]]);
    }
    $heading=$cat!==''?$cat.' reports — Research directory':'Research directory — Eviulon & Evulgare';
    render_head($heading,'Supplemental research reports and source material distinct from the fourteen official books.',$path,$graph,$cat===''?'index,follow':'noindex,follow');
    echo '<main id="content" class="shell generic-page research-directory"><p class="eyebrow">SECONDARY REFERENCE COLLECTION</p><h1>Research reports</h1><p><strong>The books are the official Eviulon collection.</strong> These reports are supplemental research for evaluating questions and external sources.</p><aside class="research-disclaimer" role="note"><strong>Research disclaimer:</strong> '.h(RESEARCH_DISCLAIMER).'</aside>';
    echo '<p class="research-directory-summary">Browse <strong>'.number_format($total).' public reports</strong> across two supplemental collections. Select a collection below or open any report directly; no search is required.</p>';
    echo '<p><a href="/">Return to the 14 official books →</a> · <a href="/search/">Search books and optionally research →</a></p>';
    echo '<nav class="research-tabs" aria-label="Browse research collections"><a href="/research/"'.($cat===''?' aria-current="page"':'').'>All reports <strong>'.number_format($total).'</strong></a> <a href="/research/?collection=Eviulon"'.($cat==='Eviulon'?' aria-current="page"':'').'>Eviulon <strong>'.(int)$counts['Eviulon'].'</strong></a> <a href="/research/?collection=Evulgare"'.($cat==='Evulgare'?' aria-current="page"':'').'>Evulgare <strong>'.(int)$counts['Evulgare'].'</strong></a></nav>';
    foreach(['Eviulon','Evulgare'] as $group){if($cat && $cat!==$group)continue;
        echo '<section class="research-group"><h2>'.h($group).' research <small>('.(int)$counts[$group].' reports)</small></h2><ol class="research-list">';
        foreach($records as $r){if($r['group']!==$group)continue;
            echo '<li><a href="'.h($r['url']).'">'.h($r['title']).'</a> <span class="research-meta">'.(int)$r['parts'].' sections · Research</span></li>';
        }
        echo '</ol></section>';
    }
    echo '</main>';render_foot();exit;
}
function research_landing(array $r): never {
    $url=$r['url'];$title=$r['title'];
    render_head($title.' — Supplemental research', $r['summary'].' '.RESEARCH_DISCLAIMER,$url,[
       ['@type'=>'Report','@id'=>absurl($url).'#research','url'=>absurl($url),
        'name'=>$title,'identifier'=>$r['id'],'description'=>$r['summary'],
        'genre'=>'Supplemental source research; not official Eviulon doctrine',
        'creativeWorkStatus'=>'supplemental_research_unverified',
        'isAccessibleForFree'=>true,'inLanguage'=>'en',
        'isPartOf'=>['@id'=>absurl('/research/').'#collection'],
        'hasPart'=>array_map(static fn($n)=>[
          '@type'=>'CreativeWork','@id'=>absurl(research_url($r,$n)).'#section',
          'name'=>$title.' — section '.$n,'url'=>absurl(research_url($r,$n)),
          'identifier'=>$r['id'].'/section-'.$n,
          'isPartOf'=>['@id'=>absurl($url).'#research']
        ],range(1,(int)$r['parts']))],
       ['@type'=>'WebPage','@id'=>absurl($url).'#webpage','url'=>absurl($url),
        'name'=>$title.' — supplemental report','mainEntity'=>['@id'=>absurl($url).'#research']],
       breadcrumbs([['Research','/research/'],[$title,$url]])]);
    echo '<main id="content" class="shell generic-page research-detail"><nav class="crumb"><a href="/">Official books</a> / <a href="/research/">Research directory</a></nav><p class="eyebrow">'.h($r['group']).' · SUPPLEMENTAL RESEARCH · NOT OFFICIAL DOCTRINE</p><h1>'.h($title).'</h1><aside class="research-disclaimer" role="note"><strong>Research disclaimer:</strong> '.h(RESEARCH_DISCLAIMER).'</aside>';
    echo '<p>'.h($r['summary']).'</p><dl class="research-source"><dt>Source file</dt><dd>'.h($r['source_file']).'</dd><dt>Source SHA-256</dt><dd><code>'.h($r['source_sha256']).'</code></dd><dt>Sections</dt><dd>'.(int)$r['parts'].'</dd></dl>';
    echo '<h2>Read this research report</h2><p>Read one section at a time. These research-section numbers are not book print-page references.</p><ol class="page-index">';
    for($n=1;$n<=$r['parts'];$n++)echo '<li><a href="'.h(research_url($r,$n)).'">'.(int)$n.'</a></li>';
    echo '</ol><p><a href="'.h(research_url($r,1)).'">Open section 1 →</a></p></main>';
    render_foot();exit;
}
function research_reader(array $r,int $n): never {
    $part=research_part($r,$n);if(!$part)send404('Research section not found');
    $url=research_url($r,$n);
    render_head($r['title'].' — Research section '.$n,'Supplemental '.$r['group'].' research. Section '.$n.' of '.$r['parts'].'. Not official doctrine. '.$r['summary'], $url,[
     ['@type'=>'WebPage','@id'=>absurl($url).'#webpage','url'=>absurl($url),
      'name'=>$r['title'].' — research section '.$n,
      'description'=>'Supplemental research section; not approved Eviulon doctrine; independent verification required.',
      'mainEntity'=>['@id'=>absurl($url).'#section']],
     ['@type'=>'CreativeWork','@id'=>absurl($url).'#section','url'=>absurl($url),
      'name'=>$r['title'].' — research section '.$n,
      'identifier'=>$r['id'].'/section-'.$n,
      'inLanguage'=>'en','isAccessibleForFree'=>true,
      'creativeWorkStatus'=>'supplemental_research_unverified',
      'description'=>'Supplemental source report section, not approved Eviulon doctrine.',
      'isPartOf'=>['@id'=>absurl($r['url']).'#research']],
     breadcrumbs([['Research','/research/'],[$r['title'],$r['url']],['Section '.$n,$url]])], 'index,follow',null,'/api/v1/research/'.$r['id'].'/parts/'.$n.'/');
    echo '<main id="content" class="shell generic-page research-reader"><nav class="crumb"><a href="/">Official books</a> / <a href="/research/">Research</a> / <a href="'.h($r['url']).'">'.h($r['title']).'</a></nav><p class="eyebrow">RESEARCH · '.h($r['group']).' · NOT OFFICIAL EVIULON DOCTRINE</p><h1>'.h($r['title']).'</h1><p class="research-position">Research section '.$n.' of '.(int)$r['parts'].'</p><aside class="research-disclaimer" role="note"><strong>Research disclaimer:</strong> '.h(RESEARCH_DISCLAIMER).'</aside>';
    echo '<nav class="research-nav" aria-label="Research sections">';if($n>1)echo '<a href="'.h(research_url($r,$n-1)).'" rel="prev">← Previous section</a>';
    echo '<a href="'.h($r['url']).'">All sections</a>';
    if($n<$r['parts'])echo '<a href="'.h(research_url($r,$n+1)).'" rel="next">Next section →</a>';
    echo '</nav><article class="research-body">'.research_linkify_html((string)$part['html']).'</article><nav class="research-nav" aria-label="Research sections">';
    if($n>1)echo '<a href="'.h(research_url($r,$n-1)).'" rel="prev">← Previous section</a>';
    echo '<a href="'.h($r['url']).'">Report overview</a>';
    if($n<$r['parts'])echo '<a href="'.h(research_url($r,$n+1)).'" rel="next">Next section →</a>';
    echo '</nav><p class="research-provenance">Source: '.h($r['source_file']).' · SHA-256: <code>'.h($r['source_sha256']).'</code></p></main>';
    render_foot();exit;
}
