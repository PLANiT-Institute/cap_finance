import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
 title: 'TCaR · 전환금융 분석 | PLANiT Institute',
 description: '기업의 설비 전환 일정과 PPA·EPC 계약별 증분비용·TCaR·ES를 비교하는 연구 도구. 기업 후보 결과, 입력 데이터, 공정 참조 실험 제공.',
 robots: { index: false, follow: false },
};
export default function RootLayout({children}:{children:React.ReactNode}) {return <html lang="ko"><body>{children}</body></html>;}
