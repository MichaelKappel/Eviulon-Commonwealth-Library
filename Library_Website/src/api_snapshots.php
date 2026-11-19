<?php
/**
 * Deterministic, public API catalog payloads shared by PHP fallback routes and
 * the prebuilt static JSON delivery layer. Never includes manuscript downloads.
 */
declare(strict_types=1);

function api_books_catalog_payload(): array {
    $results=[];
    foreach (all_books() as $b) $results[]=[
        'title'=>$b['title'],'subtitle'=>$b['subtitle'],'slug'=>$b['slug'],
        'number'=>$b['number'],'print_pages'=>$b['page_count'],
        'description'=>$b['description'],'url'=>absurl(book_url($b)),
        'api'=>absurl('/api/v1/books/'.$b['slug'].'/')
    ];
    return ['name'=>SERIES_NAME,
        'source_version'=>'Books 1–12: v2026.11.12.2; Books 13–14: v2026.11.17.54',
        'pages'=>1925,'books'=>$results,
        'format'=>'read-only HTML and JSON, one print page per record'];
}
function api_book_metadata_payload(array $b): array {
    return ['book'=>$b,'read_url'=>absurl(book_url($b)),
        'first_page'=>absurl(page_url($b,1))];
}
function api_book_toc_payload(array $b): array {
    return ['type'=>'official_eviulon_book','official'=>true,'title'=>$b['title'],
        'book_url'=>absurl(book_url($b)),
        'toc'=>array_map(static fn($x)=>array_merge($x,['canonical_url'=>absurl($x['url'])]),book_sections($b))];
}
function api_research_catalog_payload(int $page=1,int $limit=25): array {
    $all=research_records();
    return ['kind'=>'supplemental_research','official_books_url'=>BASE_URL.'/',
        'disclaimer'=>RESEARCH_DISCLAIMER,'total'=>count($all),'page'=>$page,
        'reports'=>array_slice($all,($page-1)*$limit,$limit)];
}
function api_research_metadata_payload(array $r): array {
    return ['type'=>'supplemental_research','official'=>false,
        'disclaimer'=>RESEARCH_DISCLAIMER,'report'=>$r];
}
