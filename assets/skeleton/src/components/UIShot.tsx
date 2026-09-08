/** 有真实截图就用截图，没有就回退到代码复刻的界面 */
import React from 'react';
import { Img, staticFile } from 'remotion';
import { C } from '../theme';
import { shots } from '../assets/shots';

export const UIShot: React.FC<{
  scene: string;
  width: number;
  children: React.ReactNode;
}> = ({ scene, width, children }) => {
  const shot = shots[scene];

  if (shot) {
    return (
      <div
        style={{
          width,
          borderRadius: 12,
          overflow: 'hidden',
          border: `1px solid ${C.line}`,
          boxShadow: '0 24px 70px rgba(44,40,32,.18)',
          background: '#fff',
        }}
      >
        <Img src={staticFile(shot)} style={{ display: 'block', width: '100%' }} />
      </div>
    );
  }

  return <>{children}</>;
};
