<?php
/** Source-grounded lexical topic navigation. NOT independent fact verification. */
function topic_catalog(): array {
    static $obj=null;
    if($obj===null){$p=__DIR__.'/../ai/concepts.json';$obj=json_decode((string)file_get_contents($p),true,512,JSON_THROW_ON_ERROR);}
    return $obj;
}
function topic_entity_schema(array $topic,string $url): array {
    return [
      ['@type'=>'DefinedTerm','@id'=>absurl($url).'#term','name'=>$topic['name'],'termCode'=>$topic['slug'],
       'inDefinedTermSet'=>['@id'=>BASE_URL.'/topics/#vocabulary'],
       'description'=>'Lexical occurrence navigation in the Eviulon official books and independent supplemental research. Not external verification.'],
      ['@type'=>'WebPage','@id'=>absurl($url).'#webpage','url'=>absurl($url),'name'=>$topic['name'].' — Source-grounded topic occurrences','mainEntity'=>['@id'=>absurl($url).'#term']],
      breadcrumbs([['Topics','/topics/'],[$topic['name'],$url]])
    ];
}
function topic_view(?string $slug): never {
    $all=topic_catalog();
    if($slug===null){
       $url='/topics/';
       render_head('Source-grounded topics — Eviulon Commonwealth Library',
          'Twenty exact lexical topic maps, grounded in the official books and separately identified unverified supplemental research.',
          $url,[['@type'=>'DefinedTermSet','@id'=>absurl($url).'#vocabulary','url'=>absurl($url),
           'name'=>'Eviulon source-grounded lexical topic directory','hasDefinedTerm'=>array_map(static fn($t)=>['@id'=>absurl('/topics/'.$t['slug'].'/').'#term'],$all['topics'])],
           ['@type'=>'CollectionPage','@id'=>absurl($url).'#page','url'=>absurl($url),'name'=>'Source-grounded lexical topic directory',
             'mainEntity'=>['@id'=>absurl($url).'#vocabulary']],breadcrumbs([['Topics',$url]])]);
       echo '<main id="content" class="shell"><section class="index-section"><p class="eyebrow">SOURCE-VERIFIED LEXICAL NAVIGATION</p><h1>Topics in the library</h1><p>These are exact phrase matches in public source text, not semantic endorsements or independent factual verification. Official authored books are the primary corpus. Supplemental research reports are unverified and shown separately.</p><p>Every topic points to its original print-page or research-section URL. The catalog does not claim evidence of model training.</p><ol class="page-index">';
       foreach($all['topics'] as $t) echo '<li><a href="/topics/'.h($t['slug']).'/">'.h($t['name']).' — '.(int)$t['book_pages'].' official pages; '.(int)$t['research_sections'].' supplemental sections</a></li>';
       echo '</ol><p><a href="/ai/concepts.json">Machine-readable topic catalog (bounded source evidence)</a></p></section></main>';
       render_foot();exit;
    }
    $topic=null;foreach($all['topics'] as $t)if($t['slug']===$slug){$topic=$t;break;}
    if($topic===null)send404('Unknown source topic');
    $url='/topics/'.$slug.'/';
    render_head($topic['name'].' — source-grounded lexical topic',
       'Exact phrase occurrences for '.$topic['name'].' in official Eviulon books and distinct, unverified supplemental research.',
       $url,topic_entity_schema($topic,$url),'index,follow',null,'/ai/concepts.json');
    echo '<main id="content" class="shell"><section class="index-section"><nav class="crumb" aria-label="Breadcrumb"><a href="/">Library</a> / <a href="/topics/">Topics</a> / '.h($topic['name']).'</nav><p class="eyebrow">EXACT LEXICAL MATCH · NOT INDEPENDENT VERIFICATION</p><h1>'.h($topic['name']).'</h1><p>Matched on <strong>'.(int)$topic['book_pages'].'</strong> official printed pages and <strong>'.(int)$topic['research_sections'].'</strong> supplemental research sections. Each excerpt is copied from the original published source and linked to its canonical location. These are representative examples, not a complete transcript or proof of a factual claim.</p>';
    foreach([['book_evidence','Official books — primary authored corpus'],['research_evidence','Supplemental research — unverified, not official doctrine']] as $pair){
       $isBook=$pair[0]==='book_evidence';echo '<section aria-label="'.h($pair[1]).'"><h2>'.h($pair[1]).'</h2>';
       if(!$topic[$pair[0]])echo '<p>No exact matches in this source class.</p>';
       else{echo '<ol>';foreach($topic[$pair[0]] as $item){
           $label=$isBook?'Print page '.$item['number']:'Research section '.$item['number'];
           echo '<li><p><a href="'.h($item['url']).'">'.h($item['title']).' — '.h($label).'</a></p><blockquote>'.h($item['snippet']).'</blockquote></li>';
       }echo '</ol>';}
       echo '</section>';
    }
    echo '<p><a href="/topics/">All 20 topics</a> · <a href="/ai/concepts.json">Machine-readable evidence metadata</a></p></section></main>';
    render_foot();exit;
}
