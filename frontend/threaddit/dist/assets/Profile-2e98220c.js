import{P as v,b as N,A as h,r as n,f as p,j as e,c as u,d as x,a as C,e as k,L as P,g as M,M as S}from"./index-4fc24ff5.js";import{I as F}from"./InfinitePosts-8e7aee80.js";import{Chat as _}from"./Inbox-2c6e7c88.js";import"./Post-ccc57d8f.js";j.propTypes={setModal:v.func};function j({setModal:m}){const c=N(),{user:r}=h(),[t,l]=n.useState(r.bio),[s,d]=n.useState(""),[o,g]=n.useState("image"),[b,y]=n.useState("");async function f(a){a==null||a.preventDefault();const i=new FormData;i.append("bio",t),i.append("content_type",o),i.append("content_url",b),s&&i.append("avatar",s,s.name),await x.patch("/api/user",i,{headers:{"Content-Type":"multipart/form-data"}}).then(()=>{m(!1),c.invalidateQueries({queryKey:["user",r.username]})}).catch(w=>alert(`${w.message} check your fields`))}return n.useEffect(()=>(p.setFocused(!1),()=>p.setFocused(!0)),[]),e.jsxs("div",{className:"flex flex-col p-5 space-y-5 w-5/6 rounded-md min-h-3/6 md:w-3/4 md:p-10 bg-theme-cultured",children:[e.jsxs("div",{className:"flex flex-col justify-between items-center p-4 space-y-3 bg-white rounded-xl md:flex-row md:space-y-0",children:[e.jsx("p",{children:"Updating Profile for"}),e.jsx("img",{src:r.avatar||u,className:"object-cover w-10 h-10 rounded-full md:w-14 md:h-14",alt:""}),e.jsx("p",{children:r.username})]}),e.jsxs("form",{className:"flex flex-col p-5 space-y-5 bg-white rounded-md",onSubmit:f,children:[e.jsxs("label",{htmlFor:"bio",className:"flex flex-col p-2 md:space-x-3 md:flex-row",children:[e.jsx("span",{className:"text-sm font-light",children:"Bio"}),e.jsx("textarea",{value:t,onChange:a=>l(a.target.value),type:"text",name:"bio",id:"bio",className:"w-full h-20 max-h-28 border-b border-gray-800 focus:outline-none"})]}),e.jsxs("label",{htmlFor:"media",className:"flex flex-col items-center space-y-3 md:space-y-0 md:space-x-5 md:flex-row",children:[e.jsxs("select",{className:"px-10 py-2 bg-white rounded-md border md:px-12",name:"media",id:"media",onChange:a=>g(a.target.value),children:[e.jsx("option",{value:"image",children:"Image"}),e.jsx("option",{value:"url",children:"URL"})]}),o==="image"?e.jsx("input",{onChange:a=>d(a.target.files[0]),type:"file",name:"file",accept:"image/*",id:"image",className:"w-full focus:outline-none"}):e.jsx("input",{type:"text",name:"media_url",id:"media_url",className:"p-2 w-full rounded-md border border-gray-800 focus:outline-none",onChange:a=>y(a.target.value)})]}),e.jsx("span",{className:"text-sm font-semibold text-red-500",children:"Only Add Image if you want to modify the original image if empty the original will be used."}),e.jsx("button",{onClick:f,className:"py-2 font-semibold text-white rounded-md bg-theme-orange active:scale-95",children:"Submit"})]})]})}function I(){const{logout:m,user:c}=h(),{username:r}=C(),[t,l]=n.useState(!1),{data:s,isFetching:d}=k({queryKey:["user",r],queryFn:async()=>await x.get(`/api/user/${r}`).then(o=>o.data)});return n.useEffect(()=>{switch(t){case"message":l(e.jsx(_,{sender:s,setCurChat:l,newChat:!0}));break;case"edit":l(e.jsx(j,{setModal:l}));break;case"delete":window.confirm("Are you sure you want to delete your account?")&&x.delete("/api/user").then(()=>m()),l(!1);break}},[t,s,r,m]),e.jsxs("div",{className:"flex flex-col flex-1 items-center w-full bg-theme-cultured",children:[d?e.jsx(P,{forPosts:!0}):e.jsx("div",{className:"flex flex-col items-center w-full bg-theme-cultured",children:e.jsxs("div",{className:"flex flex-col p-2 w-full bg-white rounded-md md:p-5",children:[e.jsxs("div",{className:"flex flex-col flex-1 justify-between items-center p-2 w-full rounded-md md:flex-row md:rounded-full bg-theme-cultured",children:[e.jsx("img",{src:s.avatar||u,className:"object-cover w-24 h-24 bg-white rounded-full cursor-pointer md:w-36 md:h-36",alt:"",onClick:()=>l(e.jsx("img",{src:s.avatar||u,className:"object-cover w-11/12 max-h-5/6 md:w-max md:max-h-screen",alt:""}))}),e.jsxs("div",{className:"flex flex-col flex-1 items-center w-full md:p-2",children:[e.jsxs("h1",{className:"mt-2 text-lg font-semibold md:m-0",children:["u/",s.username]}),e.jsx("p",{className:"my-4 w-11/12 text-sm text-center md:my-2 md:text-base",children:s==null?void 0:s.bio}),e.jsxs("div",{className:"flex justify-between items-center w-full md:w-11/12",children:[e.jsxs("p",{className:"text-xs md:text-sm",children:["Karma: ",s==null?void 0:s.karma.user_karma]}),e.jsxs("p",{className:"text-xs md:text-sm",children:["Cake Day On: ",new Date(s==null?void 0:s.registrationDate).toDateString()]})]})]})]}),e.jsxs("div",{className:"flex flex-col my-2 text-sm md:text-sm",children:[e.jsxs("div",{className:"flex justify-between space-x-2",children:[e.jsxs("p",{className:"",children:["Total Posts: ",s==null?void 0:s.karma.posts_count]}),e.jsxs("p",{className:"",children:["Posts Karma: ",s==null?void 0:s.karma.posts_karma]})]}),e.jsxs("div",{className:"flex justify-between space-x-2",children:[e.jsxs("p",{className:"",children:["Total Comments: ",s==null?void 0:s.karma.comments_count]}),e.jsxs("p",{className:"",children:["Comments Karma: ",s==null?void 0:s.karma.comments_karma]})]})]}),e.jsxs("select",{name:"options",id:"options",className:"p-2 mt-2 bg-white rounded-md border-2",value:t,onChange:o=>l(o.target.value),children:[e.jsx("option",{value:!1,children:"Choose an action"}),c.username===(s==null?void 0:s.username)&&e.jsxs(e.Fragment,{children:[e.jsx("option",{value:"edit",children:"Update Profile"}),e.jsx("option",{value:"delete",children:"Delete Account"})]}),e.jsx("option",{value:"message",children:"Message"})]})]})}),e.jsx(F,{apiQueryKey:s==null?void 0:s.username,linkUrl:`posts/user/${s==null?void 0:s.username}`,enabled:(s==null?void 0:s.username)!==void 0}),e.jsx(M,{children:t!==!1&&t!=="delete"&&e.jsx(S,{showModal:t,setShowModal:l,children:t})})]})}export{I as Profile,I as default};
