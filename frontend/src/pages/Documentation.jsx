import React from "react";
import {
  FileText, Server, Database, Shield, Rocket, CheckCircle2,
  ExternalLink, Layers, ArrowRight, Activity, Terminal
} from "lucide-react";

export default function Documentation() {
  const docSections = [
    {
      title: "System Architecture",
      icon: Server,
      badge: "Architecture",
      badgeColor: "bg-sky-100 text-sky-800",
      description: "Complete layout of CloudModX cloud-native infrastructure on AWS ap-south-1.",
      highlights: [
        "Amazon EC2 (t3.small) running Dockerized React & FastAPI",
        "Nginx reverse proxy on Port 80 routing to internal port 8000",
        "Amazon RDS PostgreSQL 15 in private subnets across 2 AZs",
        "Amazon S3 bucket for versioned binary artifacts",
        "AWS SSM Session Manager + CloudWatch observability",
      ],
    },
    {
      title: "Deployment & Rollback Engine",
      icon: Rocket,
      badge: "Workflow",
      badgeColor: "bg-emerald-100 text-emerald-800",
      description: "State machine orchestrating release artifact validation, automated deployment, and instant rollback.",
      highlights: [
        "Deterministic states: PENDING → RUNNING → SUCCESS / FAILED",
        "Pre-deployment artifact integrity and S3 checksum verification",
        "Granular failure capture with actionable diagnostic messages",
        "1-click Rollback restoring previous stable release in history",
        "Tamper-evident audit logging for every execution step",
      ],
    },
    {
      title: "Database Models & Schema",
      icon: Database,
      badge: "Data Model",
      badgeColor: "bg-indigo-100 text-indigo-800",
      description: "SQLAlchemy ORM models mapped to Amazon RDS PostgreSQL 15.",
      highlights: [
        "users: Identity, roles, and ownership",
        "modules: Cloud service metadata & lifecycle status",
        "module_versions: Semantic releases (e.g. v1.0.0)",
        "artifacts: S3 storage paths, byte sizes, and SHA-256 hashes",
        "deployments: Execution timestamps, environment, and error logs",
        "audit_logs: Chronological record of administrative events",
      ],
    },
    {
      title: "Security & Isolation Model",
      icon: Shield,
      badge: "Security",
      badgeColor: "bg-purple-100 text-purple-800",
      description: "Enterprise defense-in-depth isolation across compute, network, and storage layers.",
      highlights: [
        "Public ingress strictly limited to TCP Port 80 (HTTP)",
        "FastAPI backend bound exclusively to internal Docker bridge network",
        "RDS PostgreSQL is private (publicly_accessible=false, port 5432 from EC2 SG only)",
        "Zero static AWS credentials: IAM Instance Profile authentication",
        "SSH Port 22 disabled; secure terminal via AWS SSM",
      ],
    },
    {
      title: "Demo Verification & Checklist",
      icon: Activity,
      badge: "QA / Evidence",
      badgeColor: "bg-amber-100 text-amber-800",
      description: "10-step verification sequence proving end-to-end platform capabilities.",
      highlights: [
        "Dashboard health & PostgreSQL live connectivity probe",
        "Module creation → Version registration → S3 artifact upload",
        "Deployment execution with success promotion to Active",
        "Failed deployment simulation & diagnostic error capture",
        "Rollback execution restoring previous stable version",
        "Live CloudWatch alarms verification (all in OK state)",
      ],
    },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header Banner */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight flex items-center space-x-2">
            <FileText className="w-6 h-6 text-sky-600" />
            <span>CloudModX Documentation</span>
          </h2>
          <p className="text-sm text-gray-500 mt-1">
            Technical specifications, architecture blueprints, data models, and verification guides.
          </p>
        </div>
        <div className="flex items-center space-x-2 bg-sky-50 text-sky-800 text-xs px-3.5 py-1.5 rounded-lg border border-sky-200">
          <Terminal className="w-4 h-4 text-sky-600" />
          <span className="font-mono">AWS Region: ap-south-1</span>
        </div>
      </div>

      {/* Doc Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {docSections.map((sec) => {
          const Icon = sec.icon;
          return (
            <div key={sec.title} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2.5 bg-slate-50 text-slate-700 rounded-lg border border-gray-100">
                    <Icon className="w-5 h-5 text-sky-600" />
                  </div>
                  <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${sec.badgeColor}`}>
                    {sec.badge}
                  </span>
                </div>
                <h3 className="text-base font-bold text-gray-900 mb-1">{sec.title}</h3>
                <p className="text-xs text-gray-500 mb-4">{sec.description}</p>
                <ul className="space-y-2 text-xs text-gray-600">
                  {sec.highlights.map((h, i) => (
                    <li key={i} className="flex items-start space-x-2">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 mt-0.5 flex-shrink-0" />
                      <span>{h}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
