# 部署就緒 / Deployment Readiness

這份文件說明如何把本機版準備成 Render 可部署版本。它不是正式臨床上線核准，也不代表已經可以投入真實醫療環境。

This guide makes the local app deploy-ready on Render. It is not clinical production approval.

## 目前狀態 / Current State

- 本機版已可用：`Final_Check.cmd` 應回報 `final_complete`。
- 專案已加入 Render Blueprint：`render.yaml`。
- Django settings 已支援 production env：`DJANGO_DEBUG=0`、`DJANGO_SECRET_KEY`、`DATABASE_URL`。
- 尚未公開部署：目前工作區沒有 Git remote，也沒有 Render CLI 登入狀態。

查看部署下一步：

```powershell
clinical_differential_support\Deploy_Status.cmd
```

或打開本機部署操作中心：

```text
http://127.0.0.1:8000/deployment/
```

## 安全範圍 / Safety Boundary

- 僅供合格醫療專業人員作為參考支援。
- No patient data：不要輸入真實病人識別資料。
- 不提供自動診斷、治療、用藥、劑量或醫囑。
- Staff reviewer 帳號必須用互動方式建立；不要把密碼寫進檔案、環境紀錄或 Git。
- 正式臨床使用前仍需法規、隱私、資安、臨床與機構審查。

## 需要先準備 / Prerequisites

1. 將這個 repo 推到 GitHub、GitLab 或 Bitbucket。
2. 建立或登入 Render 帳號。
3. 在 Render Dashboard 選擇 Blueprint，指向 repo root 的 `render.yaml`。

先確認 scoped deployment package 是否已經可以提交：

```powershell
clinical_differential_support\Publish_Status.cmd
```

這個助手只讀取 Git 狀態，會列出需要審查、stage、commit 的 scoped files；它不會自動 `git add`、`git commit`、設定 remote 或推送。

如果還沒有 Git remote，先做這件事，不要跳過：

```powershell
clinical_differential_support\Configure_Git_Remote.cmd --remote-url <your-repo-url>
```

這個助手只設定本機 Git `origin`。它不會保存密碼或 token，不會建立雲端 repo，也不會自動 push；確認 remote 正確後，只有明確加上 `--push` 才會推送。

## Render Blueprint

`render.yaml` 會建立：

- Python web service：`clinical-differential-support`
- PostgreSQL database：`clinical-differential-support-db`
- Health check：`/health/`
- Build command：`bash ./clinical_differential_support/build.sh`
- Start command：`cd clinical_differential_support && gunicorn clinical_differential_support.wsgi:application --bind 0.0.0.0:$PORT`

## 環境變數 / Environment Variables

Render Blueprint 已處理必要值：

- `DATABASE_URL`：由 Render PostgreSQL 提供。
- `DJANGO_SECRET_KEY`：由 Render 產生，不寫入 repo。
- `DJANGO_DEBUG=0`
- `DJANGO_SECURE_SSL_REDIRECT=1`
- `DJANGO_DB_SSL_REQUIRE=1`
- `DJANGO_SECURE_HSTS_SECONDS=31536000`

可選值：

- `DJANGO_ALLOWED_HOSTS`：自訂網域時加入，例如 `clinical.example.com`。
- `DJANGO_CSRF_TRUSTED_ORIGINS`：自訂 HTTPS origin，例如 `https://clinical.example.com`。

## Build Script

`clinical_differential_support/build.sh` 會執行：

1. 安裝 requirements
2. `collectstatic --no-input`
3. `migrate --run-syncdb`
4. 載入已審核的 MVP fixtures

它不會建立 superuser、不會讀取密碼、不會列印密碼。

## 部署後第一步 / First Step After Deploy

部署完成後，在 Render Shell 互動建立 staff reviewer：

```bash
python manage.py createsuperuser
```

這一步必須由操作者手動輸入 username、email 與密碼。不要使用 committed credentials。

## 上線後檢查 / Post-Deploy Checks

打開：

```text
https://<render-service-host>/health/
https://<render-service-host>/completion/
https://<render-service-host>/review/login/
```

預期：

- `/health/` 回傳 `status: ok`
- `/completion/` 顯示 final gate 狀態
- `/review/login/` 顯示 staff login

## 本機部署檢查 / Local Deployment Checks

在本機用 production-style env 檢查：

```powershell
$env:DJANGO_DEBUG='0'
$env:DJANGO_SECRET_KEY='local-production-check-only'
$env:DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'
$env:DJANGO_SECURE_SSL_REDIRECT='0'
$env:DJANGO_DB_SSL_REQUIRE='0'
py -B .\clinical_differential_support\manage.py check --deploy
py -B .\clinical_differential_support\manage.py collectstatic --no-input
```

檢查後可清掉這些 session env：

```powershell
Remove-Item Env:\DJANGO_DEBUG
Remove-Item Env:\DJANGO_SECRET_KEY
Remove-Item Env:\DJANGO_ALLOWED_HOSTS
Remove-Item Env:\DJANGO_SECURE_SSL_REDIRECT
Remove-Item Env:\DJANGO_DB_SSL_REQUIRE
```
