import { FC } from 'react';

interface ProgressBarProps {
  progress: number;
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export const ProgressBar: FC<ProgressBarProps> = ({
  progress,
  variant = 'primary',
  size = 'md',
  showLabel = false,
  className = '',
}) => {
  const variantClasses: Record<string, string> = {
    primary: 'bg-blue-500',
    success: 'bg-green-500',
    warning: 'bg-yellow-500',
    danger: 'bg-red-500',
    info: 'bg-indigo-500',
  };

  const sizeClasses: Record<string, string> = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const clampedProgress = Math.min(Math.max(progress, 0), 100);

  return (
    <div className={`w-full ${className}`}>
      <div
        className={`w-full bg-gray-200 rounded-full overflow-hidden ${sizeClasses[size]}`}
      >
        <div
          className={`h-full ${variantClasses[variant]} transition-all duration-300 ease-out`}
          style={{ width: `${clampedProgress}%` }}
        />
      </div>
      {showLabel && (
        <p className="text-xs text-gray-600 mt-1">{Math.round(clampedProgress)}%</p>
      )}
    </div>
  );
};

export default ProgressBar;
