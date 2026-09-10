'use client';
import {useEffect,useState} from 'react';
import Research from '@/components/Research';
import Simulator from '@/components/Simulator';
import DataExplorer from '@/components/DataExplorer';
import Methodology from '@/components/Methodology';
import Introduction from '@/components/Introduction';
import './introduction.css';
const NAV=[['overview','프로젝트'],['research','전환계획 비교'],['data','데이터'],['method','모형의 원리'],['simulator','참조 실험']];
export default function Home(){
 const [active,setActive]=useState('overview');
 useEffect(()=>{function read(){const value=window.location.hash.slice(1);if(!value)setActive('overview');else if(NAV.some(([id])=>id===value))setActive(value);}read();window.addEventListener('hashchange',read);window.addEventListener('popstate',read);return()=>{window.removeEventListener('hashchange',read);window.removeEventListener('popstate',read);};},[]);
 function navigate(id:string){setActive(id);window.history.pushState(null,'',id==='overview'?window.location.pathname:`#${id}`);window.scrollTo({top:0,behavior:'instant'});}
 return <div className={`app ${active==='overview'?'project-home':''}`}><a href="#main" className="skip">본문 바로가기</a><header className="header"><button className="brand" aria-label="TCaR 프로젝트 홈" onClick={()=>navigate('overview')}><strong>PLAN<span>i</span>T</strong><span className="brand-product">TCaR</span></button><nav aria-label="분석 메뉴">{NAV.map(([id,label])=><button key={id} className={active===id?'active':''} aria-current={active===id?'page':undefined} onClick={()=>navigate(id)}>{label}</button>)}</nav><a className="related" href="https://planit.institute/" target="_blank" rel="noreferrer">연구소 ↗</a></header>{active!=='overview'&&<div className="context-bar"><button className="context-home" onClick={()=>navigate('overview')}>TCaR 프로젝트</button><span>연구 도구 <b>ALPHA 0.1</b></span></div>}<main id="main" className={active==='overview'?'intro-main':undefined}>{active==='overview'?<Introduction onNavigate={navigate}/>:active==='research'?<Research/>:active==='simulator'?<Simulator/>:active==='data'?<DataExplorer/>:<Methodology onNavigate={navigate}/>}</main><footer><div><strong>PLANiT Institute</strong><span>기업 전환계획의 비용·위험 · TCaR</span></div><div><a href="https://kets-outlook.vercel.app/" target="_blank" rel="noreferrer">K-ETS Outlook ↗</a><a href="https://planit.institute/" target="_blank" rel="noreferrer">PLANiT 홈페이지 ↗</a></div></footer></div>;
}
