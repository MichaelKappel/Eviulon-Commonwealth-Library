<?php
/* PHP built-in development server only. Apache production uses .htaccess. */
$path=urldecode(parse_url($_SERVER['REQUEST_URI']??'/',PHP_URL_PATH)?:'/');
if(preg_match('#^/(data|src|tests|tools|private|\.uai)(/|$)#i',$path) || preg_match('#^/(?:README_DEPLOY|QA_REPORT|CHANGELOG)\.md$#i',$path)){http_response_code(403);exit('Forbidden');}
// PHP's built-in test server does not supply Apache/LiteSpeed static file
// ETags and discovery-method contracts. Preserve those in QA through the
// existing fallback; real production GET/HEAD stays direct-to-web-server.
if (in_array($path, ['/robots.txt','/llms.txt','/ai/knowledge.json','/ai/source-registry.jsonld','/ai/discovery-attestation.json','/openapi.json','/feeds/books.atom'], true)
    || preg_match('#^/sitemap(?:-[A-Za-z0-9-]+)?\.xml$#',$path)) {
    require __DIR__.'/index.php';
}
// 20 lexical topic pages and index are source-rendered prebuilt static HTML.
if($path==='/topics-cache' || str_starts_with($path,'/topics-cache/')){http_response_code(403);exit('Forbidden');}
if(in_array(strtoupper($_SERVER['REQUEST_METHOD']??'GET'),['GET','HEAD'],true)
    && (string)(parse_url($_SERVER['REQUEST_URI']??'',PHP_URL_QUERY)??'')===''
    && ($path==='/topics/' || preg_match('#^/topics/([a-z0-9-]+)/$#',$path,$m))){
    $file=__DIR__.'/topics-cache/'.($path==='/topics/'?'index':$m[1]).'.html';
    if(is_file($file)){
       header('Content-Type: text/html; charset=utf-8');
       header('Cache-Control: public, max-age=3600, stale-while-revalidate=86400');
       header('X-Eviulon-Delivery: prebuilt-source-topic-html');
       $etag='"'.hash_file('sha256',$file).'"';header('ETag: '.$etag);
       header('Last-Modified: '.gmdate('D, d M Y H:i:s',filemtime($file)).' GMT');
       if(trim($_SERVER['HTTP_IF_NONE_MATCH']??'')===$etag){http_response_code(304);exit;}
       if(strtoupper($_SERVER['REQUEST_METHOD']??'GET')==='HEAD')exit;
       readfile($file);exit;
    }
}
// Do not permit direct public access to the internal HTML snapshot paths.
if($path==='/html-cache' || str_starts_with($path,'/html-cache/')) {http_response_code(403);exit('Forbidden');}
if (in_array(strtoupper($_SERVER['REQUEST_METHOD']??'GET'),['GET','HEAD'],true)
    && (string)(parse_url($_SERVER['REQUEST_URI']??'',PHP_URL_QUERY)??'')==='') {
    $rel=null;
    if(preg_match('#^/research/(eviulon|evulgare)/([a-z0-9-]+)/([1-9][0-9]*)/$#',$path,$m)) $rel="research/$m[1]/$m[2]/$m[3].html";
    else if(preg_match('#^/research/(eviulon|evulgare)/([a-z0-9-]+)/$#',$path,$m)) $rel="research/$m[1]/$m[2]/landing.html";
    else if(preg_match('#^/([a-z0-9-]+)/([1-9][0-9]*)/$#',$path,$m)) $rel="books/$m[1]/$m[2].html";
    else if(preg_match('#^/([a-z0-9-]+)/$#',$path,$m)) $rel="books/$m[1]/landing.html";
    if($rel!==null && is_file(__DIR__.'/html-cache/'.$rel)) {
       $file=__DIR__.'/html-cache/'.$rel;
       header('Content-Type: text/html; charset=utf-8');
       header('Cache-Control: public, max-age=3600, stale-while-revalidate=86400');
       header('X-Eviulon-Delivery: prebuilt-static-html');
       $etag='"'.hash_file('sha256',$file).'"';header('ETag: '.$etag);
       header('Last-Modified: '.gmdate('D, d M Y H:i:s',filemtime($file)).' GMT');
       if(trim($_SERVER['HTTP_IF_NONE_MATCH']??'')===$etag){http_response_code(304);exit;}
       if(strtoupper($_SERVER['REQUEST_METHOD']??'GET')==='HEAD')exit;
       readfile($file);exit;
    }
}
if($path!=='/' && is_file(__DIR__.$path))return false; // Native static files
// Development-only mapping equivalent to the .htaccess static rewrite rules.
// Production Apache/LiteSpeed hands these files directly to the web server.
if (in_array(strtoupper($_SERVER['REQUEST_METHOD']??'GET'),['GET','HEAD'],true)) {
    $file=null;$query=(string)(parse_url($_SERVER['REQUEST_URI']??'', PHP_URL_QUERY)??'');
    if($query==='' && $path==='/api/v1/') $file='v1/index.json';
    else if($query==='' && $path==='/api/v1/books/') $file='v1/books.json';
    else if($path==='/api/v1/research/' && $query==='') $file='v1/research-index.json';
    else if($query==='' && preg_match('#^/api/v1/books/([a-z0-9-]+)/citations/([1-9][0-9]*)/$#',$path,$m)) $file='v1/citations/books/'.$m[1].'/'.$m[2].'.json';
    else if($query==='' && preg_match('#^/api/v1/research/(eviulon|evulgare)/([a-z0-9-]+)/parts/([1-9][0-9]*)/citation/$#',$path,$m)) $file='v1/citations/research/'.$m[1].'/'.$m[2].'/'.$m[3].'.json';
    else if($query==='' && preg_match('#^/api/v1/books/([a-z0-9-]+)/toc/$#',$path,$m)) $file='v1/toc/'.$m[1].'.json';
    else if($query==='' && preg_match('#^/api/v1/books/([a-z0-9-]+)/$#',$path,$m)) $file='v1/books/'.$m[1].'.json';
    else if($query==='' && preg_match('#^/api/v1/research/(eviulon|evulgare)/([a-z0-9-]+)/$#',$path,$m)) $file='v1/research/'.$m[1].'/'.$m[2].'.json';
    if($file!==null && is_file(__DIR__.'/api-cache/'.$file)) {
        require_once __DIR__.'/src/bootstrap.php';
        header('Access-Control-Allow-Origin: *');
        header('X-Eviulon-Delivery: prebuilt-static-json');
        header('X-Robots-Tag: noindex');
        header('Link: <'.BASE_URL.'/openapi.json>; rel="service-desc"; type="application/json"');
        serve_api_snapshot_dev(__DIR__.'/api-cache/'.$file);
    }
}
require __DIR__.'/index.php';
