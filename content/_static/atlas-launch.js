/* Original Book-to-Lab handoff. All links retain the current project prefix. */
document.addEventListener("DOMContentLoaded",()=>{
  const route=location.pathname.match(/^(.*\/)book(?:\/(.*))?$/);
  if(!route)return;
  let chapter=decodeURIComponent(route[2]||"");
  if(!chapter||chapter.endsWith("/"))chapter+="index.html";
  else if(!chapter.split("/").pop().includes("."))chapter+="/index.html";
  if(!chapter.endsWith(".html")||["search.html","genindex.html"].includes(chapter))return;
  const prefix=route[1],notebook=chapter.replace(/\.html$/,".ipynb");
  const article=document.querySelector("article.bd-article");if(!article)return;
  const nav=document.createElement("nav");nav.setAttribute("aria-label","Atlas and runnable notebook");
  nav.style.cssText="display:flex;flex-wrap:wrap;gap:18px;margin:0 0 24px;font-size:.9rem";
  const home=document.createElement("a");home.href=prefix;home.textContent="← Atlas home";
  const run=document.createElement("a");run.href=prefix+"lite/lab/index.html?path="+encodeURIComponent(notebook);run.textContent="Run this notebook in Lab ↗";
  nav.append(home,run);article.prepend(nav);
});
