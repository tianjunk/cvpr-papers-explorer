# cvpr-papers-explorer

一个静态的 CVPR 论文分类浏览页，当前包含 CVPR 2026，后续可扩展到 CVPR 2025、CVPR 2027 等年份。支持按方向浏览、关键词搜索、代码链接筛选，并包含公众号入口。

## 本地更新页面

```powershell
python .\scripts\classify_papers.py
python .\scripts\build_site.py
```

生成后的静态入口是 `index.html`，公众号图片是 `mycode.png`。

## GitHub Pages 托管

本项目已包含 GitHub Pages Actions 工作流：`.github/workflows/pages.yml`。

使用方式：

1. 在 GitHub 新建一个空仓库。
2. 把本目录推送到仓库的 `main` 分支。
3. 进入仓库 `Settings -> Pages`。
4. 将 `Build and deployment` 的 `Source` 设为 `GitHub Actions`。
5. 推送后等待 Actions 完成，页面会发布到 GitHub Pages 地址。

工作流只发布：

- `index.html`
- `mycode.png`
- `.nojekyll`

`data/` 和 `scripts/` 会保留在仓库源码里，但不会作为网站资源发布。
