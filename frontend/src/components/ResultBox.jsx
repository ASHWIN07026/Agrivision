export default function ResultBox({ title, children }) {
  return (
    <div className="result-box">
      <h3 className="result-title">{title}</h3>
      {children}
    </div>
  );
}
