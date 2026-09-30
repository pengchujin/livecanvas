import React from 'react';
import {AbsoluteFill, Composition, Easing, interpolate, registerRoot, useCurrentFrame, useVideoConfig} from 'remotion';
import sample from '../data.json';

type Point = {date: string; value: number | null; sourceId: string};
type Dataset = typeof sample;
type Props = {data: Dataset};
const time = (s: string) => Date.parse(`${s}T00:00:00Z`);
const easeOut = Easing.bezier(0.23, 1, 0.32, 1);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const format = (v: number, n: number) => v.toLocaleString('en-US', {maximumFractionDigits:n, minimumFractionDigits:n});

export const Chart: React.FC<Props> = ({data}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = interpolate(frame, [0.2*fps, 2.1*fps], [0,1], clamp);
  const reveal = interpolate(frame, [0,0.2*fps], [0,1], {...clamp,easing:easeOut});
  const [low,high] = data.display.yDomain;
  const left=120, right=950, top=625, bottom=1050;
  const start=time(data.period.start), end=time(data.period.end);
  const x=(d:string)=>left+(time(d)-start)/(end-start)*(right-left);
  const y=(v:number)=>bottom-(v-low)/(high-low)*(bottom-top);
  const now=start+(end-start)*p;
  const maxGap=({daily:7,monthly:45,yearly:400}[data.period.granularity] ?? 45)*86400000;
  const firstSeries=data.series[0];
  const observed=firstSeries.points.filter(v=>v.value!==null);
  const first=observed[0], last=observed[observed.length-1];
  const peak=observed.reduce((a,b)=>b.value!>a.value!?b:a);
  const temperature=data.metric.kind==='temperature';
  const delta=last.value!-first.value!;
  const hero=temperature ? `${format(peak.value!,data.display.decimals)}°` : first.value===0 ? format(last.value!,data.display.decimals) : `${delta>=0?'+':''}${format(delta/first.value!*100,1)}%`;
  const headline=temperature ? `${firstSeries.name} · 区间最高观测 · ${peak.date}` : first.value===0 ? `${firstSeries.name} · 期末值 · ${data.metric.unit}` : `${firstSeries.name} · 区间变化 · 按实际首尾观测`;
  const path=(points:Point[])=>{
    let previous:Point|null=null;
    return points.map(point=>{
      if(point.value===null){previous=null;return '';}
      const command=previous && time(point.date)-time(previous.date)<=maxGap?'L':'M';
      previous=point;
      return `${command}${x(point.date)},${y(point.value)}`;
    }).join(' ');
  };
  const labelFont={fontSize:25,fill:'#656a75'};
  return <AbsoluteFill style={{background:'#f5f3ee',color:'#19212b',fontFamily:'"PingFang SC", "Noto Sans CJK SC", sans-serif',fontVariantNumeric:'tabular-nums'}}>
    <div style={{position:'absolute',top:76,left:82,right:82,display:'flex',justifyContent:'space-between',fontSize:23,letterSpacing:2,color:'#68716f'}}>
      <span>LIVECANVAS / 数据实况</span><span>{data.demo?'合成示例 · 非真实数据':data.asOf}</span>
    </div>
    <div style={{position:'absolute',top:155,left:82,right:82,fontSize:66,lineHeight:1.2,fontWeight:650,letterSpacing:-2}}>{data.title}</div>
    <div style={{position:'absolute',top:258,left:86,right:86,fontSize:27,color:'#667078',lineHeight:1.5}}>{data.subtitle}</div>
    <div style={{position:'absolute',top:345,left:82,fontSize:112,fontWeight:600,letterSpacing:-5,opacity:reveal,transform:`translateY(${(1-reveal)*12}px)`}}>{hero}</div>
    <div style={{position:'absolute',top:485,left:86,fontSize:25,color:'#667078'}}>{headline}</div>
    <svg width={1080} height={1440} style={{position:'absolute'}}>
      <defs><clipPath id="sweep"><rect x={left-6} y={top-20} width={(right-left)*p+12} height={bottom-top+40}/></clipPath></defs>
      <text x={left} y={top-55} {...labelFont}>{data.metric.label} / {data.metric.unit}</text>
      {Array.from({length:5},(_,i)=>low+(high-low)*i/4).map(value=><g key={value}>
        <line x1={left} x2={right} y1={y(value)} y2={y(value)} stroke="#dbdfda" strokeWidth={1}/>
        <text x={left-20} y={y(value)+8} textAnchor="end" {...labelFont}>{format(value, value%1===0?0:1)}</text>
      </g>)}
      {low<0 && high>0 && <line x1={left} x2={right} y1={y(0)} y2={y(0)} stroke="#a7afa9" strokeWidth={2}/>}
      {[0,.5,1].map((fraction,i)=>{
        const day=new Date(start+(end-start)*fraction).toISOString().slice(0,10);
        return <text key={i} x={left+(right-left)*fraction} y={bottom+48} textAnchor={i===0?'start':i===2?'end':'middle'} {...labelFont}>{day}</text>;
      })}
      {data.series.map(series=>{
        const current=series.points.filter(v=>time(v.date)<=now).at(-1);
        const fresh=current && current.value!==null && now-time(current.date)<=maxGap;
        return <g key={series.id}>
          <path d={path(series.points)} fill="none" stroke={series.color} strokeWidth={6} strokeLinejoin="round" strokeLinecap="round" clipPath="url(#sweep)"/>
          {series.points.filter(v=>v.value!==null && time(v.date)<=now).map(point=><circle key={point.date} cx={x(point.date)} cy={y(point.value!)} r={4.5} fill={series.color}/>)}
          {fresh && <circle cx={x(current.date)} cy={y(current.value!)} r={8} fill={series.color} stroke="#f5f3ee" strokeWidth={3}/>}
        </g>;
      })}
    </svg>
    <div style={{position:'absolute',top:1140,left:86,right:86,display:'flex',gap:34,fontSize:24}}>
      {data.series.map(series=>{
        const current=series.points.filter(v=>time(v.date)<=now).at(-1);
        const fresh=current && current.value!==null && now-time(current.date)<=maxGap;
        return <div key={series.id} style={{color:series.color}}>{series.name}<br/><span style={{fontSize:22,color:'#667078'}}>{fresh?`${current.date} · ${format(current.value!,data.display.decimals)} ${data.metric.unit}`:'暂无观测'}</span></div>;
      })}
    </div>
    <div style={{position:'absolute',left:86,right:86,bottom:80,borderTop:'1px solid #d3d9d3',paddingTop:23,fontSize:22,lineHeight:1.55,color:'#737a78'}}>
      <div>{data.footnote}</div><div>来源：{data.sources.map(s=>s.title).join(' / ')} · 截至 {data.asOf}</div>
    </div>
  </AbsoluteFill>;
};
registerRoot(()=> <Composition id="LiveCanvas" component={Chart} width={1080} height={1440} fps={30} durationInFrames={90} defaultProps={{data:sample}}/>);
