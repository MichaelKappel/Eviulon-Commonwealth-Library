<?php
/** Build public API snapshots. php tools/build_api_snapshots.php [--write|--check]
 * --check never writes, and is safe to use in every deploy release gate.
 */
declare(strict_types=1);
require_once __DIR__.'/../src/bootstrap.php';
require_once __DIR__.'/../src/research.php';
require_once __DIR__.'/../src/agent.php';
require_once __DIR__.'/../src/api_snapshots.php';

$mode=$argv[1]??'--check';
if (!in_array($mode,['--write','--check'],true)) {fwrite(STDERR,"Usage: php tools/build_api_snapshots.php [--write|--check]\n");exit(2);}
$root=realpath(__DIR__.'/..');
if (!$root) exit(2);
$expected=[
    'api-cache/v1/index.json'=>agent_catalog(),
    'api-cache/v1/books.json'=>api_books_catalog_payload(),
    'api-cache/v1/research-index.json'=>api_research_catalog_payload(),
];
foreach(all_books() as $book) {
    $slug=$book['slug'];
    $expected['api-cache/v1/books/'.$slug.'.json']=api_book_metadata_payload($book);
    $expected['api-cache/v1/toc/'.$slug.'.json']=api_book_toc_payload($book);
}
foreach(research_records() as $report) {
    $expected['api-cache/v1/research/'.$report['id'].'.json']=api_research_metadata_payload($report);
}
$errors=[];$bytes=0;
foreach($expected as $relative=>$payload) {
    $file=$root.'/'.$relative;
    $body=j($payload);
    $bytes+=strlen($body);
    if ($mode==='--write') {
        $parent=dirname($file);
        if (!is_dir($parent) && !mkdir($parent,0755,true) && !is_dir($parent)) { $errors[]=$relative.' directory'; continue; }
        // Atomic file replacement, so readers never see partial JSON during a build.
        $temp=tempnam($parent,'.snapshot-');
        if ($temp===false || file_put_contents($temp,$body) !== strlen($body) || !rename($temp,$file)) {
            $errors[]=$relative.' write';
            if ($temp!==false) @unlink($temp);
        } else chmod($file,0644);
    } else if (!is_file($file) || !hash_equals(hash('sha256',$body),(string)@hash_file('sha256',$file))) {
        $errors[]=$relative.' missing or stale';
    }
}
// Stale metadata from a removed report or book must never remain public.
$generated=glob($root.'/api-cache/v1/{books,toc,research/eviulon,research/evulgare}/*.json',GLOB_BRACE) ?: [];
foreach($generated as $file) if (!array_key_exists(substr($file,strlen($root)+1),$expected)) $errors[]=substr($file,strlen($root)+1).' stale extra';
echo strtoupper(substr($mode,2)).': '.count($expected).' public JSON snapshots, '.number_format($bytes).' bytes';
if($errors){echo '; FAIL '.count($errors)."\n";foreach(array_slice($errors,0,15) as $err)echo "  ".$err."\n";exit(1);}
echo "; PASS\n";
