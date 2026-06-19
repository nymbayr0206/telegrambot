import { useLayoutEffect } from "react";
import {
  Bot,
  CheckCircle2,
  ClipboardCheck,
  Eye,
  FileText,
  GitBranch,
  LayoutDashboard,
  MonitorSmartphone,
  Palette,
  Play,
  Sparkles,
} from "lucide-react";
import { Badge } from "@nous-research/ui/ui/components/badge";
import { Button } from "@nous-research/ui/ui/components/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { usePageHeader } from "@/contexts/usePageHeader";
import { cn } from "@/lib/utils";
import { PluginSlot } from "@/plugins";

const agents = [
  {
    name: "Визуал Дизайнер Агент",
    icon: Palette,
    status: "идэвхтэй",
    focus: "UI чиглэл, layout, өнгө, компонентын нийцэл",
    output: "Дизайны санал, дэлгэцийн бүтэц, засварын жагсаалт",
  },
  {
    name: "Frontend Builder Агент",
    icon: LayoutDashboard,
    status: "бэлэн",
    focus: "React/Vite код, responsive төлөв, dashboard урсгал",
    output: "Ажилладаг UI, route, компонент, build шалгалт",
  },
  {
    name: "Visual QA Агент",
    icon: Eye,
    status: "шалгана",
    focus: "Desktop/mobile харагдац, overlap, уншигдах байдал",
    output: "Алдаа, эрсдэл, screenshot нотолгоо, засварын дараалал",
  },
  {
    name: "Project Memory Агент",
    icon: FileText,
    status: "хөтөлнө",
    focus: "Шийдвэр, хийсэн ажил, хаагдаагүй асуудал",
    output: "work-log, decisions, visual-qa тэмдэглэл",
  },
];

const stages = [
  ["01", "Бриф", "Зорилго, хэрэглэгч, хүргэх үр дүнг тодорхойлно."],
  ["02", "Визуал чиглэл", "UI хэв маяг, мэдээллийн нягтрал, өнгөний зарчим тогтооно."],
  ["03", "Хэрэгжүүлэлт", "Компонент, route, state, responsive layout хийж өгнө."],
  ["04", "QA", "Харагдах алдаа, build, mobile/desktop эрсдэлийг шалгана."],
  ["05", "Хүлээлгэн өгөх", "Демо, хийсэн ажлын лог, дараагийн алхмыг бэлдэнэ."],
];

const artifacts = [
  "docs/brief.md",
  "docs/work-log.md",
  "docs/decisions.md",
  "docs/visual-qa.md",
  "skills/hermes-visual-agent-system/SKILL.md",
];

const checks = [
  "UI текст Монгол хэл дээр байна",
  "Desktop болон mobile layout эвдрэхгүй",
  "Товч, карт, хүснэгтийн текст багтана",
  "Шийдвэр болон хийсэн ажил docs-д тэмдэглэгдэнэ",
  "Build эсвэл lint шалгалтын үр дүн бүртгэгдэнэ",
];

export default function VisualAgentsPage() {
  const { setAfterTitle, setEnd, setTitle } = usePageHeader();

  useLayoutEffect(() => {
    setTitle("Визуал агент систем");
    setAfterTitle(
      <Badge tone="success" className="text-[10px]">
        Hermes project
      </Badge>,
    );
    setEnd(
      <Button size="sm" className="gap-2 whitespace-nowrap">
        <Play className="size-3.5" />
        Процесс эхлүүлэх
      </Button>,
    );
    return () => {
      setTitle(null);
      setAfterTitle(null);
      setEnd(null);
    };
  }, [setAfterTitle, setEnd, setTitle]);

  return (
    <div className="flex flex-col gap-4">
      <PluginSlot name="visual-agents:top" />

      <section className="grid gap-4 xl:grid-cols-[minmax(0,1.45fr)_minmax(320px,0.55fr)]">
        <div className="grid gap-4">
          <Card className="overflow-hidden">
            <CardContent className="p-0">
              <div className="grid gap-0 lg:grid-cols-[minmax(0,1fr)_280px]">
                <div className="p-5 sm:p-6">
                  <div className="mb-4 flex items-center gap-2 text-xs text-muted-foreground">
                    <Sparkles className="size-4 text-warning" />
                    <span>Hermes төслийн визуал ажлын удирдлага</span>
                  </div>
                  <h2 className="max-w-3xl text-2xl font-bold leading-tight text-foreground sm:text-3xl">
                    Агентууд, skill, процесс, хийсэн ажлыг нэг самбарт
                    төвлөрүүлнэ.
                  </h2>
                  <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">
                    Энэ хэсэг нь Hermes төсөл дээр визуал UI ажил төлөвлөх,
                    хэрэгжүүлэх, шалгах, баримтжуулах үндсэн workflow-г
                    Монгол хэл дээр харуулна.
                  </p>
                </div>
                <div className="grid border-t border-border bg-muted/20 p-4 lg:border-l lg:border-t-0">
                  <div className="grid grid-cols-2 gap-3 lg:grid-cols-1">
                    <Metric label="Агент" value="4" />
                    <Metric label="Үе шат" value="5" />
                    <Metric label="Artifact" value="5" />
                    <Metric label="QA чек" value="5" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-3 md:grid-cols-2">
            {agents.map((agent) => {
              const Icon = agent.icon;
              return (
                <Card key={agent.name}>
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <div className="grid size-9 shrink-0 place-items-center border border-border bg-muted/30">
                        <Icon className="size-4 text-foreground" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-start justify-between gap-2">
                          <h3 className="text-sm font-semibold leading-5 text-foreground">
                            {agent.name}
                          </h3>
                          <Badge tone="secondary" className="shrink-0 text-[10px]">
                            {agent.status}
                          </Badge>
                        </div>
                        <p className="mt-2 text-xs leading-5 text-muted-foreground">
                          {agent.focus}
                        </p>
                        <p className="mt-3 border-t border-border pt-3 text-xs leading-5 text-foreground/80">
                          {agent.output}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ClipboardCheck className="size-4" />
              QA шалгах хуудас
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            {checks.map((check) => (
              <div
                key={check}
                className="flex items-start gap-2 border border-border bg-muted/15 p-2.5 text-xs leading-5"
              >
                <CheckCircle2 className="mt-0.5 size-3.5 shrink-0 text-success" />
                <span>{check}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(300px,420px)]">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GitBranch className="size-4" />
              Процессын урсгал
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2">
              {stages.map(([step, title, description], index) => (
                <div
                  key={step}
                  className={cn(
                    "grid gap-3 border border-border bg-card/60 p-3",
                    "sm:grid-cols-[48px_minmax(0,1fr)]",
                  )}
                >
                  <div className="font-mono-ui text-sm text-muted-foreground">
                    {step}
                  </div>
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-semibold text-foreground">
                        {title}
                      </h3>
                      {index === 0 ? (
                        <Badge tone="success" className="text-[10px]">
                          эхлэл
                        </Badge>
                      ) : null}
                    </div>
                    <p className="mt-1 text-xs leading-5 text-muted-foreground">
                      {description}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MonitorSmartphone className="size-4" />
              Project artifacts
            </CardTitle>
          </CardHeader>
          <CardContent className="grid gap-2">
            {artifacts.map((artifact) => (
              <div
                key={artifact}
                className="flex items-center gap-2 border border-border bg-muted/15 px-3 py-2 font-mono-ui text-xs text-foreground/85"
              >
                <Bot className="size-3.5 shrink-0 text-muted-foreground" />
                <span className="min-w-0 truncate">{artifact}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </section>

      <PluginSlot name="visual-agents:bottom" />
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-border bg-card/70 p-3">
      <div className="font-mono-ui text-2xl font-semibold leading-none text-foreground">
        {value}
      </div>
      <div className="mt-1 text-[11px] text-muted-foreground">{label}</div>
    </div>
  );
}
