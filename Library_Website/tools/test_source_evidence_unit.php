<?php
declare(strict_types=1);
/** Offline unit regression: source-excerpt byte boundaries and fail-closed inputs. */
require_once __DIR__.'/../src/research.php';
require_once __DIR__.'/../src/evidence.php';
$total=0;$passed=0;
function check(bool $condition,string $name):void {
    global $total,$passed;$total++;
    if($condition){$passed++;echo "PASS $name\n";}
    else {echo "FAIL $name\n";}
}
function refuses(array $args):bool {
    try { evidence_parameters($args); return false; }
    catch(InvalidArgumentException){return true;}
}
$p=evidence_parameters(['q'=>'  cognitive liberty  ']);
check($p['q']==='cognitive liberty' && $p['scope']===['books'] && $p['limit']===5 && $p['match']==='all','Default contract only searches books');
check(evidence_parameters(['q'=>'machine','scope'=>'research,books'])['scope']===['books','research'],'Authority order normalized');
check(refuses(['q'=>'machine','scope'=>'books,internal']),'Unknown scope fails closed');
check(refuses(['q'=>['machine']]),'Array query rejected');
check(refuses(['q'=>'machine','scope'=>['books']]),'Array scope rejected');
check(refuses(['q'=>'machine','match'=>'vector']),'Unadvertised match method rejected');
check(refuses(['q'=>'machine','limit'=>9]),'Over-limit fails closed');
check(refuses(['q'=>'machine','limit'=>true]),'Boolean limit rejected');
check(refuses(['q'=>'machine','limit'=>'1e3']),'Exponent-string limit rejected');
check(refuses(['q'=>str_repeat('é',71)]),'140-byte query cap enforced for UTF-8');
check(refuses(['q'=>'machine' . "\0" . 'secrets']),'Direct NUL in q rejected');
$body=str_repeat('λ',150).str_repeat('🏛',30).'machine rights'.str_repeat('⚙',200);
$quote=evidence_exact_quote($body,['machine']);
$raw=$quote['text'];$start=$quote['start_byte'];$n=$quote['length_bytes'];
check(preg_match('//u',$raw)===1,'Multi-byte excerpt remains valid UTF-8');
check(substr($body,$start,$n)===$raw && $n<=480,'Byte offsets refer to literal source substring');
check(hash('sha256',$raw)===$quote['sha256'],'Digest is of source-excerpt bytes');
check($quote['has_prefix']===true && $quote['has_suffix']===true,'Truncation boundaries explicitly flagged');
$short=evidence_exact_quote('one exact page', ['exact']);
check($short['text']==='one exact page' && $short['start_byte']===0 && !$short['has_prefix'] && !$short['has_suffix'],'Short source returns exact complete text');
check(evidence_exact_quote('', ['machine'])['length_bytes']===0,'Empty source extract is safe');
echo "RESULT: $passed/$total passed\n";
exit($total===$passed?0:1);
