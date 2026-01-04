<?php return array (
  'parameters' => 
  array (
    'database_host' => 'some-mysql',  // ✅ MySQL 컨테이너 이름
    'database_port' => '3306',
    'database_name' => 'prestashop805',
    'database_user' => 'root',
    'database_password' => 'admin',
    'database_prefix' => 'ps_',
    'database_engine' => 'InnoDB',
    'mailer_transport' => 'smtp',
    'mailer_from' => 'noreply@localhost',
    'secret' => 'changeme_secret',
    'ps_caching' => 'CacheMemcache',
    'ps_cache_enable' => false,
    'ps_creation_date' => '2025-10-27',
    'locale' => 'en-US',
    'cookie_key' => 'changeme_cookie_key',
    'cookie_iv' => 'abcd1234',
    'new_cookie_key' => 'changeme_new_cookie_key',
  ),
);
