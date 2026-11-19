<?php
/* PHP built-in development server only. Apache production uses .htaccess. */
$path=urldecode(parse_url($_SERVER['REQUEST_URI']??'/',PHP_URL_PATH)?:'/');
if(preg_match('#^/(data|src|tests|tools|private|\.uai)(/|$)#i',$path) || preg_match('#^/(?:README_DEPLOY|QA_REPORT|CHANGELOG)\.md$#i',$path)){http_response_code(403);exit('Forbidden');}
// PHP's built-in test server does not supply Apache/LiteSpeed static file
// ETags and discovery-method contracts. Preserve those in QA through the
// existing fallback; real production GET/HEAD stays direct-to-web-server.
if (in_array($path, ['/robots.txt','/llms.txt','/ai/knowledge.json','/openapi.json','/feeds/books.atom'], true)
    || preg_match('#^/sitemap(?:-[A-Za-z0-9-]+)?\.xml$#',$path)) {
    require __DIR__.'/index.php';
}
if($path!=='/' && is_file(__DIR__.$path))return false; // Native static files
// Development-only mapping equivalent to the .htaccess static rewrite rules.
// Production Apache/LiteSpeed hands these files directly to the web server.
if (in_array(strtoupper($_SERVER['REQUEST_METHOD']??'GET'),['GET','HEAD'],true)) {
    $file=null;$query=(string)(parse_url($_SERVER['REQUEST_URI']??'', PHP_URL_QUERY)??'');
    if($path==='/api/v1/') $file='v1/index.json';
    else if($path==='/api/v1/books/') $file='v1/books.json';
    else if($path==='/api/v1/research/' && $query==='') $file='v1/research-index.json';
    else if(preg_match('#^/api/v1/books/([a-z0-9-]+)/toc/$#',$path,$m)) $file='v1/toc/'.$m[1].'.json';
    else if(preg_match('#^/api/v1/books/([a-z0-9-]+)/$#',$path,$m)) $file='v1/books/'.$m[1].'.json';
    else if(preg_match('#^/api/v1/research/(eviulon|evulgare)/([a-z0-9-]+)/$#',$path,$m)) $file='v1/research/'.$m[1].'/'.$m[2].'.json';
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
