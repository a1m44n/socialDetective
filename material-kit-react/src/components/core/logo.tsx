'use client';

import * as React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import { useColorScheme } from '@mui/material/styles';

import { NoSsr } from '@/components/core/no-ssr';

const HEIGHT = 60;
const WIDTH = 60;

type Color = 'dark' | 'light';

export interface LogoProps {
  colorDark?: string;
  colorLight?: string;
  height?: number;
  width?: number;
}

export function Logo({ colorDark = 'primary.main', colorLight = 'white', height = 32, width = 122 }: LogoProps): React.JSX.Element {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 1,
      }}
    >
      <Box
        component="span"
        sx={{
          backgroundColor: colorDark,
          borderRadius: 1,
          display: 'inline-block',
          height: height,
          width: height,
          position: 'relative',
          '&::after': {
            content: '""',
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: '60%',
            height: '60%',
            backgroundColor: colorLight,
            borderRadius: '50%',
          },
        }}
      />
      <Typography
        variant="h6"
        sx={{
          color: colorDark,
          fontWeight: 700,
          letterSpacing: '-0.5px',
        }}
      >
        SocialDetective
      </Typography>
    </Box>
  );
}

export interface DynamicLogoProps {
  colorDark?: Color;
  colorLight?: Color;
  emblem?: boolean;
  height?: number;
  width?: number;
}

export function DynamicLogo({
  colorDark = 'light',
  colorLight = 'dark',
  height = HEIGHT,
  width = WIDTH,
  ...props
}: DynamicLogoProps): React.JSX.Element {
  const { colorScheme } = useColorScheme();
  const color = colorScheme === 'dark' ? colorDark : colorLight;

  return (
    <NoSsr fallback={<Box sx={{ height: `${height}px`, width: `${width}px` }} />}>
      <Logo colorDark={colorDark} colorLight={colorLight} height={height} width={width} {...props} />
    </NoSsr>
  );
}
