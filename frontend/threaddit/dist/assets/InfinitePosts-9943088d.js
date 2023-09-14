import{Q as j,k as v,l as N,n as w,o as $,q as k,s as M,r as C,j as e,L as Q,m as B,g as O,P as b,d as R}from"./index-d6e0ea8c.js";import{P as T}from"./Post-f017db6c.js";class _ extends j{constructor(s,r){super(s,r)}bindMethods(){super.bindMethods(),this.fetchNextPage=this.fetchNextPage.bind(this),this.fetchPreviousPage=this.fetchPreviousPage.bind(this)}setOptions(s,r){super.setOptions({...s,behavior:v()},r)}getOptimisticResult(s){return s.behavior=v(),super.getOptimisticResult(s)}fetchNextPage({pageParam:s,...r}={}){return this.fetch({...r,meta:{fetchMore:{direction:"forward",pageParam:s}}})}fetchPreviousPage({pageParam:s,...r}={}){return this.fetch({...r,meta:{fetchMore:{direction:"backward",pageParam:s}}})}createResult(s,r){var u,i,m,n,a,o;const{state:l}=s,g=super.createResult(s,r),{isFetching:x,isRefetching:d}=g,h=x&&((u=l.fetchMeta)==null||(i=u.fetchMore)==null?void 0:i.direction)==="forward",t=x&&((m=l.fetchMeta)==null||(n=m.fetchMore)==null?void 0:n.direction)==="backward";return{...g,fetchNextPage:this.fetchNextPage,fetchPreviousPage:this.fetchPreviousPage,hasNextPage:N(r,(a=l.data)==null?void 0:a.pages),hasPreviousPage:w(r,(o=l.data)==null?void 0:o.pages),isFetchingNextPage:h,isFetchingPreviousPage:t,isRefetching:d&&!h&&!t}}}function E(p,s,r){const u=$(p,s,r);return k(u,_)}S.propTypes={linkUrl:b.string,apiQueryKey:b.string,forSaved:b.bool,enabled:b.bool};function S({linkUrl:p,apiQueryKey:s,forSaved:r=!1,enabled:u=!0}){const[i,m]=M(),n=i.get("sortBy")||"top",a=i.get("duration")||"alltime",{data:o,isFetching:l,hasNextPage:g,fetchNextPage:x}=E({queryKey:["posts",s,n,a],queryFn:async({pageParam:t=0})=>await R.get(`/api/${p}?limit=20&offset=${t*20}&sortby=${n}&duration=${a}`).then(c=>c.data),enabled:u,getNextPageParam:(t,c)=>{if(!(t.length<20))return c.length}});C.useEffect(()=>{const t=c=>{const{scrollTop:f,scrollHeight:y,clientHeight:P}=c.target.scrollingElement;y-f<=P*2&&g&&!l&&x()};return window.addEventListener("scroll",t),()=>{window.removeEventListener("scroll",t)}},[x,l,g]);function d(t){i.set("duration",t),m(i)}function h(t){i.set("sortBy",t),m(i)}return e.jsxs("div",{id:"main-content",className:"flex w-full flex-col flex-1 p-2 space-y-3 rounded-lg m-0.5 bg-theme-cultured md:bg-white md:m-3",children:[!r&&e.jsxs("header",{className:"flex justify-between items-center",children:[e.jsxs("div",{className:"flex items-center space-x-2 md:hidden",children:[e.jsx("span",{children:"Sort by"}),e.jsxs("select",{name:"sort",id:"sort",className:"p-2 px-4 bg-white rounded-md md:bg-theme-cultured",onChange:t=>h(t.target.value),value:n,children:[e.jsx("option",{value:"top",children:"Top"}),e.jsx("option",{value:"hot",children:"Hot"}),e.jsx("option",{value:"new",children:"New"})]})]}),e.jsxs("div",{className:"flex items-center space-x-2 md:hidden",children:[e.jsx("span",{children:"Of"}),e.jsxs("select",{name:"duration",id:"duration",className:"p-2 px-4 bg-white rounded-md md:bg-theme-cultured",onChange:t=>d(t.target.value),value:a,children:[e.jsx("option",{value:"day",children:"Day"}),e.jsx("option",{value:"week",children:"Week"}),e.jsx("option",{value:"month",children:"Month"}),e.jsx("option",{value:"year",children:"Year"}),e.jsx("option",{value:"alltime",children:"All Time"})]})]}),e.jsxs("ul",{className:"hidden space-x-2 list-none md:flex",children:[e.jsx("li",{className:`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${a==="day"&&"bg-theme-gray-blue"}`,onClick:()=>d("day"),children:"Today"}),e.jsx("li",{className:`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${a==="week"&&"bg-theme-gray-blue"}`,onClick:()=>d("week"),children:"Week"}),e.jsx("li",{className:`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${a==="month"&&"bg-theme-gray-blue"}`,onClick:()=>d("month"),children:"Month"}),e.jsx("li",{className:`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${a==="alltime"&&"bg-theme-gray-blue"}`,onClick:()=>d("alltime"),children:"All"})]}),e.jsxs("ul",{className:"hidden mr-5 space-x-5 list-none md:flex",children:[e.jsx("li",{className:`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${n==="hot"&&"bg-theme-gray-blue"}`,onClick:()=>h("hot"),children:"Hot"}),e.jsx("li",{className:`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${n==="new"&&"bg-theme-gray-blue"}`,onClick:()=>h("new"),children:"New"}),e.jsx("li",{className:`p-2 hover:bg-theme-gray-blue rounded-md px-4 text-lg cursor-pointer ${n==="top"&&"bg-theme-gray-blue"}`,onClick:()=>h("top"),children:"Top"})]})]}),l&&e.jsx(Q,{forPosts:!0}),(o==null?void 0:o.pages[0].length)===0&&e.jsx(B.div,{initial:{opacity:0,y:10},animate:{opacity:1,y:0},transition:{duration:.25},children:e.jsxs("p",{className:"p-5 bg-white rounded-xl border-2 md:text-base hover:shadow-sm border-theme-gray-blue",children:["No posts with this filter were found, ",e.jsx("br",{className:"md:hidden"}),"Be the first to add one!"]})}),e.jsx("div",{className:"flex flex-col space-y-2 md:space-y-3",children:o==null?void 0:o.pages.map((t,c)=>e.jsx("ul",{className:"flex flex-col space-y-2 md:space-y-3",children:e.jsx(O,{initial:c==0,children:t==null?void 0:t.map((f,y)=>e.jsx(T,{post:f,postIndex:y},f.post_info.id))})},c))})]})}export{S as I};