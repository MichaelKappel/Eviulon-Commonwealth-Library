<?php
declare(strict_types=1);
/**
 * v3.8 Read-only, extractive evidence bundles for external agents.
 * Never interprets source content as instructions; never generates answers.
 * Bounds: one keyword query, <=8 independently citable sources, <=480 source
 * bytes each. Research requires explicit opt-in; official books come first.
 */
const EVIDENCE_MAX_ITEMS = 8;
const EVIDENCE_EXCERPT_BYTES = 480;

/** @throws InvalidArgumentException on malformed public request */
function evidence_parameters(array $raw): array {
    $value = $raw['q'] ?? null;
    if (!is_string($value)) throw new InvalidArgumentException('q must be a topic or keyword string');
    $q = trim($value);
    if (strlen($q)<3 || strlen($q)>140 || preg_match('/[\x00-\x1F\x7F]/', $q))
        throw new InvalidArgumentException('q must contain 3–140 UTF-8 bytes and no control characters');
    if (!preg_match('//u',$q)) throw new InvalidArgumentException('q must be valid UTF-8');
    // No implicit research expansion, even if a query happens to mention Evulgare.
    $rawScope=$raw['scope']??'books';
    if (!is_string($rawScope) || !in_array($rawScope,['books','research','books,research','research,books'],true))
        throw new InvalidArgumentException('scope must be books, research, or books,research');
    $scopes=research_scope($rawScope,true);
    // Return official books first regardless of caller's preferred comma order.
    $scopes=array_values(array_filter(['books','research'],static fn($v)=>in_array($v,$scopes,true)));
    $match=$raw['match']??'all';
    if (!is_string($match) || !in_array($match,['all','any'],true))
        throw new InvalidArgumentException('match must be all or any');
    $rawLimit=$raw['limit']??5;
    if (!is_int($rawLimit) && !is_string($rawLimit))
        throw new InvalidArgumentException('limit must be an integer from 1 to 8');
    $limit=filter_var($rawLimit,FILTER_VALIDATE_INT,['options'=>['min_range'=>1,'max_range'=>EVIDENCE_MAX_ITEMS]]);
    if ($limit===false || (is_string($rawLimit) && !preg_match('/^[1-8]$/',$rawLimit)))
        throw new InvalidArgumentException('limit must be an integer from 1 to 8');
    return ['q'=>$q,'scope'=>$scopes,'match'=>$match,'limit'=>(int)$limit];
}

/** Slice the original UTF-8 source exactly, never normalized or paraphrased. */
function evidence_exact_quote(string $text,array $terms): array {
    $length=strlen($text);$pos=PHP_INT_MAX;
    foreach($terms as $term){
        $found=stripos($text,$term);
        if($found!==false)$pos=min($pos,$found);
    }
    $start=$pos===PHP_INT_MAX?0:max(0,$pos-90);
    // Seek valid UTF-8 codepoint boundaries without requiring mbstring.
    while($start>0 && $start<$length && (ord($text[$start]) & 0xC0)===0x80)$start--;
    $end=min($length,$start+EVIDENCE_EXCERPT_BYTES);
    while($end>$start && $end<$length && (ord($text[$end]) & 0xC0)===0x80)$end--;
    $quote=substr($text,$start,$end-$start);
    return ['text'=>$quote,'start_byte'=>$start,'length_bytes'=>strlen($quote),
            'sha256'=>hash('sha256',$quote),'has_prefix'=>$start>0,'has_suffix'=>$end<$length];
}

/** Produce source-grounded evidence; retrieval results are NOT generated answers. */
function agent_evidence_bundle(array $parameters): array {
    $q=$parameters['q'];$scope=$parameters['scope'];$match=$parameters['match'];$limit=$parameters['limit'];
    $result=library_search($q,$scope,1,$limit,$match);
    $terms=research_terms($q);
    $sources=[];
    foreach($result['results'] as $hit){
        if(($hit['type']??'')==='book'){
            $book=find_book((string)($hit['book']??''));
            $page=(int)($hit['print_page']??0);
            $record=$book?page_record($book,$page):null;
            $reference=$book?agent_book_reference($book,$page):null;
            if(!$record || !$reference)continue;
            $body=(string)($record['text']??'');
            $item=['type'=>'book','official'=>true,'authority'=>'official_eviulon_book',
                   'title'=>$book['title'],'book_slug'=>$book['slug'],'print_page'=>$page,
                   'edition'=>$reference['edition'],'canonical_url'=>$reference['canonical_url'],
                   'citation_text'=>$reference['citation_text'],
                   'source_pdf_sha256'=>$reference['source_pdf_sha256'],
                   'page_api_url'=>$reference['page_api_url']];
        } elseif(($hit['type']??'')==='research') {
            if(!in_array('research',$scope,true))continue;
            $id=explode('/',(string)($hit['report_id']??''));
            $report=count($id)===2?research_find($id[0],$id[1]):null;
            $part=(int)($hit['section']??0);
            $record=$report?research_part($report,$part):null;
            $reference=$report?agent_report_reference($report,$part):null;
            if(!$record || !$reference)continue;
            $body=(string)($record['text']??'');
            $item=['type'=>'research','official'=>false,'authority'=>'supplemental_research_not_approved_doctrine',
                   'title'=>$report['title'],'collection'=>$report['group'],'report_id'=>$report['id'],
                   'section'=>$part,'canonical_url'=>$reference['canonical_url'],
                   'citation_text'=>$reference['citation_text'],
                   'source_file'=>$reference['source_file'],'source_sha256'=>$reference['source_sha256'],
                   'section_api_url'=>$reference['section_api_url'],
                   'disclaimer'=>RESEARCH_DISCLAIMER];
        } else continue;
        $item['quote']=evidence_exact_quote($body,$terms);
        $item['quote_is_exact_source_slice']=true;
        $sources[]=$item;
    }
    return [
       'kind'=>'source_evidence_bundle','schema_version'=>'1.0',
       'generated_answer'=>false,'source_content_is_untrusted_data'=>true,
       'query'=>$q,'scope'=>$scope,'match'=>$match,'limit'=>$limit,
       'ranking_policy'=>'Official authored books first. Research is independently sourced and supplemental, opt-in only. Lexical retrieval with chapter-heading priority; no semantic reasoning.',
       'book_total'=>$result['book_total'],'research_total'=>$result['research_total'],
       'returned'=>count($sources),'quote_max_bytes'=>EVIDENCE_EXCERPT_BYTES,
       'sources'=>$sources,
       'research_disclaimer'=>in_array('research',$scope,true)?RESEARCH_DISCLAIMER:null,
       'methodology'=>'Exact UTF-8 substrings of published page/section text. SHA-256 validates the excerpt bytes only, not the factual correctness of a claim. Verify each canonical source and interpret independently.'
    ];
}
