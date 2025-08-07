import React, { ReactNode } from 'react';

interface AdminProviderProps {
  children: ReactNode;
}

export function AdminProvider({ children }: AdminProviderProps): JSX.Element {
  return <div>{children}</div>;
}
