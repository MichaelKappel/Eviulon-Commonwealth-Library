<?php
/**
 * Presentation-only URL linkification for approved supplemental research HTML.
 *
 * The immutable research/parts JSON records are the source of truth. Imported
 * HTML already includes thousands of anchors; only previously unlinked plain
 * text nodes are modified. Do NOT add framework/DOM-extension dependencies:
 * the existing PHP shared-host deployment does not require ext-dom.
 */

declare(strict_types=1);

/**
 * Trim prose punctuation without breaking balanced URL parentheses, e.g.
 * Wikipedia /wiki/Some_title_(concept) followed by sentence punctuation.
 * @return array{0:string,1:string} URL, trailing punctuation
 */
function research_url_separate_punctuation(string $candidate): array {
    $suffix='';
    while ($candidate !== '') {
        $last=substr($candidate,-1);
        $strip=in_array($last,['.',',',';',':','!','?','`'],true);
        if ($last===')') $strip=substr_count($candidate,')')>substr_count($candidate,'(');
        if ($last===']') $strip=substr_count($candidate,']')>substr_count($candidate,'[');
        if ($last==='}') $strip=substr_count($candidate,'}')>substr_count($candidate,'{');
        if (!$strip) break;
        $suffix=$last.$suffix;
        $candidate=substr($candidate,0,-1);
    }
    return [$candidate,$suffix];
}

/** Linkify only web URLs (never javascript:, file:, data: or untrusted HTML). */
function research_linkify_text_node(string $text): string {
    if (stripos($text,'http://')===false && stripos($text,'https://')===false && stripos($text,'www.')===false) return $text;
    $pattern='~(?<![\pL\pN_/@])(?:https?://|www\.)[^\s<>"\'\x{2010}-\x{2015}\x{2018}\x{2019}\x{201C}\x{201D}]+~iu';
    $result=preg_replace_callback($pattern,static function(array $match): string {
        // A URL in escaped JSON/HTML is often followed by &quot; or &gt;.
        // Those entities are delimiters, unlike &amp; in genuine query strings.
        $candidate=$match[0];$entityTail='';
        if (preg_match('~&(?:quot|apos|lt|gt|nbsp|mdash|ndash|hellip|lsquo|rsquo|ldquo|rdquo|#(?:34|39)|#x(?:22|27));~i',$candidate,$entity,PREG_OFFSET_CAPTURE)) {
            $entityTail=substr($candidate,$entity[0][1]);
            $candidate=substr($candidate,0,$entity[0][1]);
        }
        [$raw,$punctuation]=research_url_separate_punctuation($candidate);
        $trailing=$punctuation.$entityTail;
        $decoded=html_entity_decode($raw,ENT_QUOTES|ENT_HTML5,'UTF-8');
        // Markdown URL escapes are display artifacts, not part of web URLs.
        $decoded=str_replace(['\\_','\\-','\\~'],['_','-','~'],$decoded);
        $target=str_starts_with(strtolower($decoded),'www.')?'https://'.$decoded:$decoded;
        if (strlen($target)>4096 || !filter_var($target,FILTER_VALIDATE_URL))return $match[0];
        $parsed=parse_url($target);
        if ($parsed===false || !in_array(strtolower($parsed['scheme']??''),['https','http'],true)
            || empty($parsed['host']) || isset($parsed['user']) || isset($parsed['pass']))return $match[0];
        // Raw display text is already escaped HTML text from the original report.
        // Do not re-escape it (which would turn &amp; into visible &amp;).
        return '<a href="'.htmlspecialchars($target,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8').
            '" target="_blank" rel="noopener noreferrer external">'.$raw.'</a>'.$trailing;
    },$text);
    return $result ?? $text;
}

/**
 * HTML-token-aware presentation pass: never transform tag attributes, existing
 * anchors, code samples, scripts, SVG, or comments. Tokenization is safe here
 * because the input comes from a known Markdown-to-HTML publication pipeline.
 * No source record or index is rewritten.
 */
function research_linkify_html(string $html): string {
    if (!preg_match('~(?:https?://|www\.)~i',$html)) return $html;
    $chunks=preg_split('~(<!--.*?-->|<![^>]*>|<\/?[A-Za-z][^>]*>)~s',$html,-1,PREG_SPLIT_DELIM_CAPTURE);
    if ($chunks===false) return $html;
    $protected=['a','pre','code','kbd','samp','script','style','textarea','svg'];
    $void=['area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'];
    $stack=[];$out='';
    foreach ($chunks as $part) {
        if (str_starts_with($part,'<') && preg_match('~^<(/?)([A-Za-z][A-Za-z0-9:-]*)\b[^>]*>$~s',$part,$m)) {
            $name=strtolower($m[2]);
            if ($m[1]==='/') {
                for ($i=count($stack)-1;$i>=0;--$i)if ($stack[$i]===$name){$stack=array_slice($stack,0,$i);break;}
            } elseif (!in_array($name,$void,true) && !str_ends_with(rtrim($part),'/>')) {
                $stack[]=$name;
            }
            $out.=$part;
        } elseif (str_starts_with($part,'<') && (str_starts_with($part,'<!--') || str_starts_with($part,'<!'))) {
            $out.=$part;
        } elseif (array_intersect($stack,$protected)) {
            $out.=$part;
        } else {
            $out.=research_linkify_text_node($part);
        }
    }
    return $out;
}
