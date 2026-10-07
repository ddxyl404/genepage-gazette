import Link from "next/link";

export default function NotFound() {
  return (
    <main className="page page--index">
      <header className="masthead">
        <div className="masthead__brand">
          <h1 className="masthead__title">
            GenePage Gazette
            <span className="masthead__title-zh">基因简报</span>
          </h1>
        </div>
        <hr className="rule-double" />
        <p className="index-lead">本期未收录该基因。</p>
        <p>
          <Link href="/">返回今日目录</Link>
        </p>
      </header>
    </main>
  );
}
