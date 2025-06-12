'use client';

import * as React from 'react';
import { useRouter } from 'next/navigation';
import { zodResolver } from '@hookform/resolvers/zod';
import Button from '@mui/material/Button';
import FormControl from '@mui/material/FormControl';
import FormHelperText from '@mui/material/FormHelperText';
import OutlinedInput from '@mui/material/OutlinedInput';
import Stack from '@mui/material/Stack';
import Typography from '@mui/material/Typography';
import InputAdornment from '@mui/material/InputAdornment';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import { Controller, useForm } from 'react-hook-form';
import { z as zod } from 'zod';
import PersonIcon from '@mui/icons-material/Person';
import LockIcon from '@mui/icons-material/Lock';

import { authClient } from '@/lib/auth/client';
import { useUser } from '@/hooks/use-user';

const schema = zod.object({
  email: zod.string().min(1, { message: 'Email is required' }).email(),
  password: zod.string().min(1, { message: 'Password is required' }),
  role: zod.enum(['admin', 'investigator', 'viewer'], { required_error: 'Role is required' }),
});

type Values = zod.infer<typeof schema>;

const defaultValues = { email: '', password: '', role: 'investigator' } satisfies Values;

export function SignInForm(): React.JSX.Element {
  const router = useRouter();
  const { checkSession } = useUser();
  const [showPassword, setShowPassword] = React.useState<boolean>(false);
  const [isPending, setIsPending] = React.useState<boolean>(false);

  const {
    control,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<Values>({ defaultValues, resolver: zodResolver(schema) });

  const onSubmit = React.useCallback(
    async (values: Values): Promise<void> => {
      setIsPending(true);
      const { error } = await authClient.signInWithPassword(values);
      if (error) {
        setError('root', { type: 'server', message: error });
        setIsPending(false);
        return;
      }
      await checkSession?.();
      router.refresh();
    },
    [checkSession, router, setError]
  );

  return (
    <Stack
      spacing={3}
      alignItems="center"
      sx={{
        width: '100%',
        maxWidth: 340,
        p: 4,
        background: 'rgba(35,36,58,0.85)',
        borderRadius: 4,
        boxShadow: '0 8px 32px rgba(35,36,58,0.25)',
      }}
    >
      <Typography
        variant="h5"
        sx={{
          fontWeight: 800,
          color: '#fff',
          letterSpacing: 1,
          mb: 0.5,
          textTransform: 'uppercase',
          textAlign: 'center',
        }}
      >
        SocialDetective
      </Typography>
      <Typography
        variant="subtitle1"
        color="#b0b3c6"
        sx={{ fontWeight: 400, fontSize: 16, textAlign: 'center', mb: 2 }}
      >
        Social media investigation made easy.
      </Typography>
      <form onSubmit={handleSubmit(onSubmit)} style={{ width: '100%' }}>
        <Stack spacing={2}>
          <Controller
            control={control}
            name="email"
            render={({ field }) => (
              <FormControl error={Boolean(errors.email)} fullWidth>
                <OutlinedInput
                  {...field}
                  label="Email address"
                  type="email"
                  placeholder="Email address"
                  sx={{
                    background: 'transparent',
                    color: '#fff',
                    borderRadius: 2,
                    '& input': { color: '#fff' },
                    '& fieldset': {
                      borderColor: '#444',
                    },
                    '&:hover fieldset': {
                      borderColor: '#ff3576',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#ff3576',
                    },
                  }}
                  startAdornment={
                    <InputAdornment position="start">
                      <PersonIcon sx={{ color: '#b0b3c6' }} />
                    </InputAdornment>
                  }
                />
                {errors.email ? (
                  <FormHelperText error>{errors.email.message}</FormHelperText>
                ) : null}
              </FormControl>
            )}
          />
          <Controller
            control={control}
            name="password"
            render={({ field }) => (
              <FormControl error={Boolean(errors.password)} fullWidth>
                <OutlinedInput
                  {...field}
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Password"
                  sx={{
                    background: 'transparent',
                    color: '#fff',
                    borderRadius: 2,
                    '& input': { color: '#fff' },
                    '& fieldset': {
                      borderColor: '#444',
                    },
                    '&:hover fieldset': {
                      borderColor: '#ff3576',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#ff3576',
                    },
                  }}
                  startAdornment={
                    <InputAdornment position="start">
                      <LockIcon sx={{ color: '#b0b3c6' }} />
                    </InputAdornment>
                  }
                  endAdornment={
                    <InputAdornment position="end">
                      <span
                        style={{ cursor: 'pointer', color: '#b0b3c6' }}
                        onClick={() => setShowPassword((show) => !show)}
                      >
                        {showPassword ? '🙈' : '👁️'}
                      </span>
                    </InputAdornment>
                  }
                />
                {errors.password ? (
                  <FormHelperText error>{errors.password.message}</FormHelperText>
                ) : null}
              </FormControl>
            )}
          />
          <Controller
            control={control}
            name="role"
            render={({ field }) => (
              <FormControl error={Boolean(errors.role)} fullWidth>
                <Select
                  {...field}
                  displayEmpty
                  sx={{
                    background: 'transparent',
                    color: '#fff',
                    borderRadius: 2,
                    '& .MuiSelect-icon': { color: '#b0b3c6' },
                    '& fieldset': {
                      borderColor: '#444',
                    },
                    '&:hover fieldset': {
                      borderColor: '#ff3576',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#ff3576',
                    },
                  }}
                  inputProps={{
                    sx: { color: '#fff' },
                  }}
                >
                  <MenuItem value="investigator">Investigator</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="viewer">Viewer</MenuItem>
                </Select>
                {errors.role ? (
                  <FormHelperText error>{errors.role.message}</FormHelperText>
                ) : null}
              </FormControl>
            )}
          />
          {errors.root ? (
            <Typography color="error" sx={{ fontWeight: 500, textAlign: 'center' }}>
              {errors.root.message}
            </Typography>
          ) : null}
          <Button
            disabled={isPending}
            type="submit"
            variant="contained"
            size="large"
            fullWidth
            sx={{
              borderRadius: 99,
              background: 'linear-gradient(90deg, #ff3576 0%, #ff6381 100%)',
              color: '#fff',
              fontWeight: 700,
              fontSize: 18,
              boxShadow: '0 2px 8px rgba(255,53,118,0.15)',
              mt: 1,
              '&:hover': {
                background: 'linear-gradient(90deg, #e82e6b 0%, #e85c7a 100%)',
              },
            }}
          >
            {isPending ? 'Signing in...' : 'Sign in'}
          </Button>
        </Stack>
      </form>
    </Stack>
  );
}
