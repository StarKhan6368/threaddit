import{A as r,u as i,a as o,j as s}from"./index-d6e0ea8c.js";import{I as m}from"./InfinitePosts-9943088d.js";import{T as n}from"./ThreadsSidebar-d406fc22.js";import"./Post-f017db6c.js";function p(){const{isAuthenticated:a}=r(),t=i(),e=o();return e.feedName=="home"&&!a?t("/login"):s.jsxs("div",{className:"flex flex-1 max-w-full bg-theme-cultured",children:[s.jsx(n,{}),s.jsx(m,{linkUrl:`posts/${e.feedName}`,apiQueryKey:e.feedName})]})}export{p as Feed,p as default};