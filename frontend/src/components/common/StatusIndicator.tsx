import React from 'react';
import { ServiceStatus } from '../../types';
import { SERVICE_STATUS_COLORS, SERVICE_STATUS_ICONS } from '../../utils/constants';

export interface StatusIndicatorProps {
  status: ServiceStatus;
}

export function StatusIndicator({ status }: StatusIndicatorProps) {
  const colorClass = SERVICE_STATUS_COLORS[status.status];
  const icon = SERVICE_STATUS_ICONS[status.status];
  
  return (
    <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-gray-50">
      <div className="flex items-center gap-3">
        <span className="text-lg">{icon}</span>
        <div>
          <div className="font-medium text-gray-900">{status.name}</div>
          {status.details && (
            <div className="text-sm text-gray-500">{status.details}</div>
          )}
        </div>
      </div>
      <div className="text-right">
        <div className={`text-sm font-medium ${colorClass}`}>
          {status.status.toUpperCase()}
        </div>
        {status.latency_ms !== undefined && (
          <div className="text-xs text-gray-500">
            {status.latency_ms}ms
          </div>
        )}
        {status.vector_count !== undefined && (
          <div className="text-xs text-gray-500">
            {status.vector_count.toLocaleString()} vectors
          </div>
        )}
        {status.pending_jobs !== undefined && (
          <div className="text-xs text-gray-500">
            {status.pending_jobs} pending
          </div>
        )}
      </div>
    </div>
  );
}
