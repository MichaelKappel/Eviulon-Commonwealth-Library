<?php
/** Regression and corpus coverage suite for presentation-only report URL links. */
declare(strict_types=1);
require_once __DIR__.'/../src/research_links.php';
$checks=0;
function check_link(bool $pass,string $name):void {
    global $checks;
    if (!$pass){fwrite(STDERR,"FAIL: $name\n");exit(1);} ++$checks;
}
$cases=[
 ['plain URL','<p>Reference: https://example.com/a/b.</p>','href="https://example.com/a/b"'],
 ['URL with a query entity','<td>https://example.com/?a=1&amp;b=2</td>','href="https://example.com/?a=1&amp;b=2"'],
 ['bare www','<p>Read www.example.com/abc</p>','href="https://www.example.com/abc"'],
 ['parenthesized link','<p>(https://example.org/p), next</p>','href="https://example.org/p"'],
 ['balanced Wikipedia-style brackets','<p>https://example.org/wiki/Test_(concept).</p>','href="https://example.org/wiki/Test_(concept)"'],
 ['nested text and table','<li><strong>Docs:</strong> https://example.org/guide</li>','href="https://example.org/guide"'],
 ['em-dash separator','<p>https://example.org/article—are now public</p>','href="https://example.org/article"'],
 ['HTML entity em-dash','<p>https://example.org/article&mdash;are now public</p>','href="https://example.org/article"'],
 ['HTML-escaped code quotes','<p>&quot;https://example.org/schema&quot;,</p>','href="https://example.org/schema"'],
 ['escaped markdown underscore','<li>https://example.org/my\\_file</li>','href="https://example.org/my_file"'],
 ['research citation inline','<li>Intro: https://example.org/page#section</li>','href="https://example.org/page#section"'],
];
foreach($cases as [$name,$before,$expected]){
 $after=research_linkify_html($before);
 check_link(str_contains($after,$expected),$name);
 check_link(str_contains($after,'rel="noopener noreferrer external"'),'secure external anchor: '.$name);
}
$unmodified=[
 'existing anchor'=>'<p><a href="https://existing.org/v1">https://existing.org/v1</a></p>',
 'tag attribute'=>'<p data-url="https://attribute.example/">No external link</p>',
 'code snippet'=>'<pre><code>curl https://samples.example.org</code></pre>',
 'nested code'=>'<p><code>https://example.org/code</code> real https://example.org/reference</p>',
 'HTML comment'=>'<!-- https://example.org/comment -->',
 'style content'=>'<style>.a{background:url(https://example.org/image)}</style>',
 'script content'=>'<script>const url="https://example.org/script";</script>',
 'non-HTTP protocol'=>'<p>javascript:alert(1) file:///etc/passwd</p>',
 'invalid host'=>'<p>https://</p>',
];
foreach($unmodified as $name=>$source){
 $target=research_linkify_html($source);
 if ($name==='nested code') {
    check_link(str_contains($target,'<code>https://example.org/code</code>'),'nested code preservation');
    check_link(str_contains($target,'href="https://example.org/reference"'),'nested code outside link');
 } else check_link($source===$target,$name.' unchanged');
}
check_link(research_linkify_html('<p>https://example.org/docs</p>')===research_linkify_html(research_linkify_html('<p>https://example.org/docs</p>')),'idempotence');
check_link(!str_contains(research_linkify_html('<p>https://example.com\" onclick=\"alert(1)</p>'),'href="https://example.com\" onclick'), 'no attribute injection');

// Check all actual report segments and ensure only presentation markup changes.
$files=glob(__DIR__.'/../data/research/parts/*/*/*.json')?:[];
check_link(count($files)===1553,'expected complete research corpus (1553 sections)');
$originalAnchors=0;$addedAnchors=0;$changedFiles=0;
foreach($files as $path){
    $data=json_decode((string)file_get_contents($path),true);
    check_link(is_array($data)&&is_string($data['html']??null)&&is_string($data['text']??null),'valid source record '.basename($path));
    $html=$data['html'];$converted=research_linkify_html($html);
    $originalAnchors+=substr_count($html,'<a ');
    $added=substr_count($converted,'rel="noopener noreferrer external"');
    if($added>0){$addedAnchors+=$added;$changedFiles++;}
    check_link(substr_count($converted,'<a ')===substr_count($html,'<a ')+$added,'preserved source anchors '.basename($path));
    check_link(strip_tags($converted)===strip_tags($html),'unchanged displayed source text '.basename($path));
    check_link(substr_count($converted,'</a>')===substr_count($html,'</a>')+$added,'no new unbalanced links '.basename($path));
}
check_link($addedAnchors>=100,'material coverage of formerly unlinked URLs');
check_link($originalAnchors>=8000,'pre-existing references remain preserved');
fwrite(STDOUT, "PASS: $checks assertions; ".count($files)." source sections scanned; ".$originalAnchors." existing anchors preserved; ".$addedAnchors." URLs converted in $changedFiles sections.\n");
