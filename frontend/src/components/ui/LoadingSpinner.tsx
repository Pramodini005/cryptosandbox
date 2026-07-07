export default function LoadingSpinner({ size = 20, className = '' }: { size?: number; className?: string }) {
  return (<svg className={`animate-spin ${className}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" width={size} height={size}><circle className="opacity-25" cx="12" cy="12" r="10" stroke="#00ff88" strokeWidth="4" /><path className="opacity-75" fill="#00ff88" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>);
}
