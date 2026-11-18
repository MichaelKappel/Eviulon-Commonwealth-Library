<?php
/**
 * Copy this file to data/monitor-config.php and set a PHP password hash below.
 * Generate the hash on your local computer or hosting shell:
 * php -r 'echo password_hash("REPLACE_WITH_A_LONG_SECRET", PASSWORD_DEFAULT), PHP_EOL;'
 * Never paste the raw password here or into a public repository.
 * HTTPS is required for safe HTTP Basic Authentication.
 */
return [
    'username' => 'admin',
    'password_hash' => 'REPLACE_WITH_GENERATED_PASSWORD_HASH',
];
