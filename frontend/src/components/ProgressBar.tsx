export default function ProgressBar({ value }: { value: number }) {
  return (
    <div aria-label="progress" className="progress" role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={100}>
      <div className="progress-inner" style={{ width: `${Math.min(100, Math.max(0, value))}%` }} />
      <span className="progress-label">{value}%</span>
    </div>
  )
}