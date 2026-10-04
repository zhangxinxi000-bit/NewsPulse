$ErrorActionPreference = "Stop"
$base = "http://127.0.0.1:8000"
$pass = 0; $fail = 0

function Check([string]$name, [bool]$ok, [string]$detail = "") {
    if ($ok) { $script:pass++; Write-Host "  [OK] $name" }
    else { $script:fail++; Write-Host "  [FAIL] $name $detail" }
}

Write-Host "== 1. health =="
$r = Invoke-RestMethod -Uri "$base/" -Method Get
Check "GET /" ($r.message -like "*running*")

Write-Host "== 2. register =="
$token = ""
try {
    $r = Invoke-RestMethod -Uri "$base/api/user/register" -Method Post -ContentType "application/json" -Body '{"username":"demo_user","email":"demo@example.com","password":"secret123"}'
    Check "register ok" ($r.code -eq 200)
    $token = $r.data.token
} catch {
    # 用户已存在（重复运行）：改用登录
    $r = Invoke-RestMethod -Uri "$base/api/user/login" -Method Post -ContentType "application/json" -Body '{"username":"demo_user","email":"demo@example.com","password":"secret123"}'
    Check "user exists, login instead" ($r.code -eq 200)
    $token = $r.data.token
}
Check "token returned" (-not [string]::IsNullOrEmpty($token))
try {
    Invoke-RestMethod -Uri "$base/api/user/register" -Method Post -ContentType "application/json" -Body '{"username":"demo_user","email":"demo@example.com","password":"secret123"}' | Out-Null
    Check "duplicate register rejected" $false
} catch { Check "duplicate register rejected" ($_.Exception.Response.StatusCode.value__ -eq 400) }

Write-Host "== 3. login =="
$r = Invoke-RestMethod -Uri "$base/api/user/login" -Method Post -ContentType "application/json" -Body '{"username":"demo_user","email":"demo@example.com","password":"secret123"}'
Check "login ok" ($r.code -eq 200)
$token = $r.data.token
try {
    Invoke-RestMethod -Uri "$base/api/user/login" -Method Post -ContentType "application/json" -Body '{"username":"demo_user","email":"demo@example.com","password":"wrongpass"}' | Out-Null
    Check "wrong password rejected" $false
} catch { Check "wrong password rejected" ($_.Exception.Response.StatusCode.value__ -eq 401) }
try {
    Invoke-RestMethod -Uri "$base/api/user/register" -Method Post -ContentType "application/json" -Body '{"username":"bad_email","email":"not-an-email","password":"secret123"}' | Out-Null
    Check "bad email rejected" $false
} catch { Check "bad email rejected" ($_.Exception.Response.StatusCode.value__ -eq 422) }

$headers = @{ Authorization = "Bearer $token" }

Write-Host "== 4. user info =="
$r = Invoke-RestMethod -Uri "$base/api/user/info" -Method Get -Headers $headers
Check "get user info" ($r.data.username -eq "demo_user")
try {
    Invoke-RestMethod -Uri "$base/api/user/info" -Method Get | Out-Null
    Check "no token -> 401" $false
} catch { Check "no token -> 401" ($_.Exception.Response.StatusCode.value__ -eq 401) }
$r = Invoke-RestMethod -Uri "$base/api/user/update" -Method Put -Headers $headers -ContentType "application/json" -Body '{"nickname":"xiao ming","bio":"FastAPI learner"}'
Check "update user info" ($r.data.nickname -eq "xiao ming")

Write-Host "== 5. news =="
$r = Invoke-RestMethod -Uri "$base/api/news/categories" -Method Get
Check "categories (>=5)" ($r.data.Count -ge 5)
$r = Invoke-RestMethod -Uri "$base/api/news/list?categoryId=1&page=1&pageSize=2" -Method Get
Check "list filtered + paged" ($r.data.list.Count -eq 2 -and $r.data.total -ge 2)
$r = Invoke-RestMethod -Uri "$base/api/news/list" -Method Get
Check "list all (>=10)" ($r.data.total -ge 10)
$r = Invoke-RestMethod -Uri "$base/api/news/detail?id=1" -Method Get
Check "news detail" ($r.data.id -eq 1)
Check "detail has relatedNews" ($null -ne $r.data.relatedNews)
$v1 = (Invoke-RestMethod -Uri "$base/api/news/detail?id=1" -Method Get).data.views
$v2 = (Invoke-RestMethod -Uri "$base/api/news/detail?id=1" -Method Get).data.views
Check "views increase" ($v2 -gt $v1)
try {
    Invoke-RestMethod -Uri "$base/api/news/detail?id=99999" -Method Get | Out-Null
    Check "missing news -> 404" $false
} catch { Check "missing news -> 404" ($_.Exception.Response.StatusCode.value__ -eq 404) }

Write-Host "== 6. favorite =="
$r = Invoke-RestMethod -Uri "$base/api/favorite/check?newsId=1" -Method Get -Headers $headers
Check "favorite check (false)" ($r.data.isFavorite -eq $false)
$r = Invoke-RestMethod -Uri "$base/api/favorite/add" -Method Post -Headers $headers -ContentType "application/json" -Body '{"news_id":1}'
Check "favorite add" ($r.code -eq 200)
try {
    Invoke-RestMethod -Uri "$base/api/favorite/add" -Method Post -Headers $headers -ContentType "application/json" -Body '{"news_id":1}' | Out-Null
    Check "duplicate favorite rejected" $false
} catch { Check "duplicate favorite rejected" ($_.Exception.Response.StatusCode.value__ -eq 400) }
$r = Invoke-RestMethod -Uri "$base/api/favorite/check?newsId=1" -Method Get -Headers $headers
Check "favorite check (true)" ($r.data.isFavorite -eq $true)
$r = Invoke-RestMethod -Uri "$base/api/favorite/list" -Method Get -Headers $headers
Check "favorite list (1)" ($r.data.total -eq 1)
$r = Invoke-RestMethod -Uri "$base/api/favorite/remove?newsId=1" -Method Delete -Headers $headers
Check "favorite remove" ($r.code -eq 200)

Write-Host "== 7. history =="
$r = Invoke-RestMethod -Uri "$base/api/history/add" -Method Post -Headers $headers -ContentType "application/json" -Body '{"news_id":2}'
Check "history add" ($r.code -eq 200)
$r = Invoke-RestMethod -Uri "$base/api/history/list" -Method Get -Headers $headers
Check "history list (1)" ($r.data.total -eq 1)
$hid = $r.data.list[0].id
$r = Invoke-RestMethod -Uri "$base/api/history/delete/$hid" -Method Delete -Headers $headers
Check "history delete one" ($r.code -eq 200)
Invoke-RestMethod -Uri "$base/api/history/add" -Method Post -Headers $headers -ContentType "application/json" -Body '{"news_id":3}' | Out-Null
$r = Invoke-RestMethod -Uri "$base/api/history/clear" -Method Delete -Headers $headers
Check "history clear" ($r.code -eq 200)

Write-Host "== 8. auth guard =="
try {
    Invoke-RestMethod -Uri "$base/api/favorite/add" -Method Post -ContentType "application/json" -Body '{"news_id":1}' | Out-Null
    Check "favorite no token -> 401" $false
} catch { Check "favorite no token -> 401" ($_.Exception.Response.StatusCode.value__ -eq 401) }

Write-Host "== 9. ai chat =="
$r = Invoke-RestMethod -Uri "$base/api/ai/chat" -Method Post -ContentType "application/json" -Body '{"question":"hello"}'
Check "ai returns notice" ($null -ne $r.data.answer -and $r.data.answer -like "*API Key*")

Write-Host ""
Write-Host "RESULT: $pass passed, $fail failed"
if ($fail -gt 0) { exit 1 } else { exit 0 }
