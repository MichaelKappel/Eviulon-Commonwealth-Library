<?php
/* PHP built-in development server only. Apache production uses .htaccess. */
$path=urldecode(parse_url($_SERVER['REQUEST_URI']??'/',PHP_URL_PATH)?:'/');
if(preg_match('#^/(data|src|tests|tools|private|\.uai)(/|$)#i',$path)){http_response_code(403);exit('Forbidden');}
if($path!=='/' && is_file(__DIR__.$path) && !in_array($path, ['/robots.txt','/llms.txt','/ai/knowledge.json'], true) && !preg_match('#^/sitemap(?:-[A-Za-z0-9-]+)?\.xml$#',$path))return false;
require __DIR__.'/index.php';
