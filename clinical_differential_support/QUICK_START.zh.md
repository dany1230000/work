# 快速開始

這份文件只回答一件事：現在要照哪個順序做。

目前狀態：

- Final Verification Gate：`ready_for_final_verification`
- 最新驗收證據：`verified`
- 本機尚未建立 staff reviewer 帳號

## 最快入口

先判斷整個專案是否已經是本機最終版：

```powershell
clinical_differential_support\Final_Check.cmd
```

或打開網頁版：

```text
http://127.0.0.1:8000/completion/
```

它會直接顯示：

- final_complete 或 manual_setup_required
- exit code
- 完成條件
- 目前唯一下一步
- 要執行的命令
- Launch Control URL

注意：這個入口只彙整狀態，不會建立帳號、列印密碼或保存密碼。

如果只想看下一步：

在 PowerShell 執行：

```powershell
clinical_differential_support\Next_Step.cmd
```

或在檔案總管雙擊：

```text
clinical_differential_support\Next_Step.cmd
```

下一步助手會直接顯示：

- 現在下一步
- exit code
- 要執行的命令
- Launch Control URL

注意：這個入口只顯示下一步，不會建立帳號、列印密碼或保存密碼。

## 下一步

現在做這個：步驟 1/6。

## 步驟 1/6：建立本機 staff reviewer 帳號

狀態：現在

執行：

```powershell
clinical_differential_support\Create_Staff_Reviewer.cmd
```

這會啟動 Django `createsuperuser` 互動提示。你會在本機手動輸入 username、email 與密碼；系統不會自動建立、列印或保存密碼。

進階 shell fallback：

```powershell
py -B .\clinical_differential_support\manage.py createsuperuser
```

注意：只建立本機測試帳號，不要使用真實工作密碼。

## 步驟 2/6：確認最終驗收證據

狀態：已完成

目前 evidence 已經是 `verified`。如果之後狀態變成不是 verified，再執行：

```powershell
py -B .\clinical_differential_support\scripts\record_final_verification_evidence.py --overwrite
```

## 步驟 3/6：啟動本機 server

狀態：等待步驟 1 完成

執行：

```powershell
clinical_differential_support\Start_Local_Server.cmd
```

啟動後先看網頁導覽：

```text
http://127.0.0.1:8000/launch/
```

## 步驟 4/6：登入 staff reviewer

狀態：等待步驟 1 和步驟 3 完成

打開：

```text
http://127.0.0.1:8000/review/login/
```

## 步驟 5/6：查看 Next Action Workbench

狀態：等待登入完成

打開：

```text
http://127.0.0.1:8000/review/next-actions/
```

用途：確認系統現在建議的下一個專案動作。

## 步驟 6/6：查看 Final Verification Gate 並下載交接包

狀態：等待登入完成

先打開 Final Verification Gate：

```text
http://127.0.0.1:8000/review/final-verification/
```

需要交接時下載 handoff bundle：

```text
http://127.0.0.1:8000/review/exports/handoff-bundle.zip
```

## 只想看目前狀態

看網頁版：

```text
http://127.0.0.1:8000/launch/
```

看最終版完成判斷：

```text
http://127.0.0.1:8000/completion/
```

執行：

```powershell
py -B .\clinical_differential_support\scripts\local_launch_status.py
```

或使用新版下一步助手：

```powershell
clinical_differential_support\Next_Step.cmd
```

或使用最終版完成判斷：

```powershell
clinical_differential_support\Final_Check.cmd
```

## 部署就緒階段

如果本機最終版已完成，下一階段是部署就緒，不是直接正式臨床上線。

先看：

```text
clinical_differential_support\DEPLOYMENT.md
```

它會說明 Render Blueprint、`render.yaml`、必要環境變數、部署後 staff reviewer 建立方式，以及為什麼目前不能把「可部署」說成「已公開部署完成」。

只想知道部署下一步，執行：

```powershell
clinical_differential_support\Deploy_Status.cmd
```

如果部署操作中心顯示 `review_commit_publish_package`，先執行：

```powershell
clinical_differential_support\Publish_Status.cmd
```

它只讀取 scoped Git 狀態，會列出需要審查、stage、commit 的 deployment package 檔案；它不會自動 `git add`、`git commit`、設定 remote 或推送。

如果部署操作中心顯示 `create_git_remote`，先在 GitHub、GitLab 或 Bitbucket 建立空 repo，然後執行：

```powershell
clinical_differential_support\Configure_Git_Remote.cmd --remote-url <your-repo-url>
```

這個助手只驗證 URL 並設定 `origin`。它不會保存密碼或 token，不會建立雲端 repo，也不會自動 push；只有明確加上 `--push` 才會推送。

或打開：

```text
http://127.0.0.1:8000/deployment/
```
