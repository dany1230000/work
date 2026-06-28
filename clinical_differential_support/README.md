# 臨床鑑別支援 MVP

Clinical Differential Support MVP

這個專案是本機 clinician-reference 工具。它提供結構化主訴頁面、staff 內容治理、下一步工作台、最終驗收證據與交接包。它不是正式臨床部署系統。

## 先看這份 / Start Here

請先看：

[QUICK_START.zh.md](QUICK_START.zh.md)

那份文件只回答三件事：

1. 下一步要做什麼
2. 要開哪個網址
3. 要跑哪個命令

## 安全範圍 / Safety Scope

- 僅供合格醫療專業人員作為參考支援。
- 不提供診斷、治療、用藥、劑量或醫囑。
- 不取代臨床判斷。
- 不要輸入真實病人識別資料。
- 正式使用前仍需法規、隱私、資安、臨床與機構審查。

## 本機啟動 / Local Launch

最快判斷專案是否最終完成：

```powershell
clinical_differential_support\Final_Check.cmd
```

也可以直接打開：

```text
http://127.0.0.1:8000/completion/
```

這個入口只彙整本機完成條件、exit code、下一步、命令與 URL；它不會建立帳號、列印密碼或保存密碼。

如果顯示 `manual_setup_required` 且下一步是建立 staff reviewer，請執行：

```powershell
clinical_differential_support\Create_Staff_Reviewer.cmd
```

這個入口會啟動 Django `createsuperuser` 互動提示。帳號、email 與密碼都由你在本機手動輸入；系統不會自動建立、列印或保存密碼。進階 shell fallback 是：

```powershell
py -B .\clinical_differential_support\manage.py createsuperuser
```

只看下一步：

```powershell
clinical_differential_support\Next_Step.cmd
```

也可以直接雙擊：

```text
clinical_differential_support\Next_Step.cmd
```

這個入口只顯示目前下一步、exit code、命令與 Launch Control URL。

啟動網頁：

```powershell
clinical_differential_support\Start_Local_Server.cmd
```

啟動後會打開：

```text
http://127.0.0.1:8000/launch/
```

只查看目前下一步的 shell 版本：

```powershell
py -B .\clinical_differential_support\scripts\local_setup_assistant.py
```

輸出 JSON：

```powershell
py -B .\clinical_differential_support\scripts\local_setup_assistant.py --json
```

## 主要網址 / Main URLs

- 首頁 / Home: `http://127.0.0.1:8000/`
- 啟動導覽 / Launch Guide: `http://127.0.0.1:8000/launch/`
- 最終版完成判斷 / Final Project Gate: `http://127.0.0.1:8000/completion/`
- Staff 登入 / Staff login: `http://127.0.0.1:8000/review/login/`
- 下一步工作台 / Next Action Workbench: `http://127.0.0.1:8000/review/next-actions/`
- 最終驗收 / Final Verification Gate: `http://127.0.0.1:8000/review/final-verification/`
- 交接包 / Handoff bundle: `http://127.0.0.1:8000/review/exports/handoff-bundle.zip`

## 完整驗證 / Verification

```powershell
py -B .\clinical_differential_support\manage.py test -v 2
py -B .\clinical_differential_support\manage.py check
py -B .\clinical_differential_support\scripts\smoke_check.py --base-url http://127.0.0.1:8000
py -B .\clinical_differential_support\scripts\record_final_verification_evidence.py --overwrite
```

## 交接包 / Handoff

```powershell
py -B .\clinical_differential_support\scripts\export_handoff_bundle.py --output handoff-bundle.zip --overwrite
py -B .\clinical_differential_support\scripts\verify_handoff_bundle.py handoff-bundle.zip
```

## 部署就緒 / Deployment Readiness

部署說明在 [DEPLOYMENT.md](DEPLOYMENT.md)。

目前已加入 Render Blueprint：repo root 的 `render.yaml`。這代表專案已具備部署檔案與 production env 設定，但不代表已經公開上線；實際部署前仍需要 Git remote、Render 帳號、secret/env 管理，以及正式臨床、法規、隱私與資安審查。

查看下一個部署步驟：

```powershell
clinical_differential_support\Deploy_Status.cmd
```

如果下一步是 `review_commit_publish_package`，先執行：

```powershell
clinical_differential_support\Publish_Status.cmd
```

這個助手只讀取 scoped Git 狀態，會列出需要審查、stage、commit 的 deployment package 檔案；它不會自動 `git add`、`git commit`、設定 remote 或推送。

如果下一步是 `create_git_remote`，先在 GitHub、GitLab 或 Bitbucket 建立空 repo，然後執行：

```powershell
clinical_differential_support\Configure_Git_Remote.cmd --remote-url <your-repo-url>
```

這個助手會驗證 URL 並設定 `origin`。它不會建立雲端 repo、不會保存密碼或 token，也不會 push；只有你明確加上 `--push` 時才會執行 `git push`。

或打開：

```text
http://127.0.0.1:8000/deployment/
```
