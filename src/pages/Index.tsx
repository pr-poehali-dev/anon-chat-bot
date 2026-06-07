import { useState } from "react";
import Icon from "@/components/ui/icon";

const HERO_IMG = "https://cdn.poehali.dev/projects/0f758643-a4f1-42bb-b83f-f32926c86302/files/b447826d-8396-43fb-b715-59abbf1e8545.jpg";

const features = [
  {
    icon: "UserRound",
    color: "pink",
    title: "Анкета игрока",
    desc: "Ник из Avakin Life, фото, пол, ориентация и возраст — всё в одном профиле"
  },
  {
    icon: "ShieldOff",
    color: "purple",
    title: "100% анонимность",
    desc: "Твой ID скрыт — переписка идёт через бота, никто не узнает кто ты"
  },
  {
    icon: "Heart",
    color: "cyan",
    title: "Лайки и матчи",
    desc: "Листай анкеты, ставь лайки — и получай взаимные совпадения"
  },
  {
    icon: "MessageCircle",
    color: "pink",
    title: "Анонимный чат",
    desc: "Общайся в защищённом чате. Бот пересылает сообщения, скрывая отправителя"
  },
  {
    icon: "Camera",
    color: "purple",
    title: "Фото в анкете",
    desc: "Загрузи своё фото из Avakin Life — покажи своего персонажа миру"
  },
  {
    icon: "Flag",
    color: "cyan",
    title: "Жалобы и безопасность",
    desc: "Фильтрация мата, автоблокировка по жалобам, модерация контента"
  },
];

const steps = [
  { num: "01", title: "Открой бота", desc: "Найди @AvaMatchBot в Telegram и нажми /start" },
  { num: "02", title: "Создай анкету", desc: "Введи ник из Avakin Life, фото, пол и возраст" },
  { num: "03", title: "Листай анкеты", desc: "Просматривай профили игроков и ставь лайки" },
  { num: "04", title: "Общайся анонимно", desc: "При взаимном лайке — начинай чат через бота" },
];

const profiles = [
  { name: "StarQueen_Ava", age: 19, gender: "Девушка", orientation: "Гетеро", likes: 142, emoji: "👑" },
  { name: "NightWolf_X", age: 22, gender: "Парень", orientation: "Гетеро", likes: 89, emoji: "🐺" },
  { name: "CrystalMoon", age: 17, gender: "Девушка", orientation: "Би", likes: 211, emoji: "🌙" },
  { name: "AvaKing777", age: 20, gender: "Парень", orientation: "Гетеро", likes: 67, emoji: "⚡" },
];

type ColorType = "pink" | "purple" | "cyan";

const colorMap: Record<ColorType, { border: string; text: string; bg: string }> = {
  pink: { border: "neon-border-pink", text: "neon-text-pink", bg: "rgba(255,45,155,0.1)" },
  purple: { border: "neon-border-purple", text: "neon-text-purple", bg: "rgba(184,41,255,0.1)" },
  cyan: { border: "neon-border-cyan", text: "neon-text-cyan", bg: "rgba(0,212,255,0.1)" },
};

export default function Index() {
  const [activeProfile, setActiveProfile] = useState(0);
  const [liked, setLiked] = useState<Record<number, boolean>>({});

  const handleLike = (idx: number) => {
    setLiked(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      {/* Фоновая сетка */}
      <div
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(184,41,255,0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(184,41,255,0.06) 1px, transparent 1px)
          `,
          backgroundSize: "40px 40px",
        }}
      />
      {/* Градиентные пятна */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full opacity-20"
          style={{ background: "radial-gradient(circle, #b829ff 0%, transparent 70%)" }} />
        <div className="absolute top-[30%] right-[-15%] w-[400px] h-[400px] rounded-full opacity-15"
          style={{ background: "radial-gradient(circle, #ff2d9b 0%, transparent 70%)" }} />
        <div className="absolute bottom-[-10%] left-[30%] w-[350px] h-[350px] rounded-full opacity-10"
          style={{ background: "radial-gradient(circle, #00d4ff 0%, transparent 70%)" }} />
      </div>

      {/* HEADER */}
      <header className="relative z-10 flex items-center justify-between px-6 py-4 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full flex items-center justify-center"
            style={{ background: "linear-gradient(135deg, #ff2d9b, #b829ff)" }}>
            <span className="text-white text-lg font-bold font-orbitron">A</span>
          </div>
          <span className="font-orbitron font-bold text-xl tracking-widest neon-text-pink">AVA<span className="neon-text-cyan">MATCH</span></span>
        </div>
        <nav className="hidden md:flex items-center gap-8">
          {["Функции", "Как работает", "Анкеты"].map(item => (
            <a key={item} href={`#${item}`} className="text-sm text-white/60 hover:text-white transition-colors font-rubik tracking-wide">
              {item}
            </a>
          ))}
        </nav>
        <a href="https://t.me/AvaMatchBot" target="_blank" rel="noopener noreferrer"
          className="btn-neon-pink px-5 py-2 rounded-full text-sm font-orbitron font-bold text-white cursor-pointer">
          Открыть бота
        </a>
      </header>

      {/* HERO */}
      <section className="relative z-10 pt-16 pb-20 px-6 text-center">
        <div className="max-w-5xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-8 animate-fade-in-up"
            style={{ animationDelay: "0.1s", opacity: 0 }}>
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            <span className="text-xs font-rubik text-white/70">Бот онлайн · Avakin Life Dating</span>
          </div>

          <h1 className="font-orbitron font-black text-5xl md:text-7xl mb-6 leading-tight animate-fade-in-up"
            style={{ animationDelay: "0.2s", opacity: 0 }}>
            <span className="neon-text-pink">АНОНИМНЫЕ</span>
            <br />
            <span className="text-white">ЗНАКОМСТВА</span>
            <br />
            <span className="neon-text-purple">AVAKIN LIFE</span>
          </h1>

          <p className="text-lg md:text-xl text-white/60 font-rubik max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-in-up"
            style={{ animationDelay: "0.35s", opacity: 0 }}>
            Находи друзей и романтических партнёров среди игроков Avakin Life. Полная анонимность, безопасность и геймерская атмосфера.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up"
            style={{ animationDelay: "0.5s", opacity: 0 }}>
            <a href="https://t.me/AvaMatchBot" target="_blank" rel="noopener noreferrer"
              className="btn-neon-pink px-8 py-4 rounded-full font-orbitron font-bold text-white text-sm tracking-wide inline-flex items-center gap-2 justify-center">
              <Icon name="Send" size={18} />
              Начать в Telegram
            </a>
            <button className="px-8 py-4 rounded-full font-orbitron font-bold text-sm tracking-wide text-white/80 glass-card neon-border-purple hover:bg-white/5 transition-all inline-flex items-center gap-2 justify-center">
              <Icon name="Play" size={18} />
              Как это работает
            </button>
          </div>

          {/* Статистика */}
          <div className="grid grid-cols-3 gap-6 max-w-lg mx-auto mt-16 animate-fade-in-up"
            style={{ animationDelay: "0.65s", opacity: 0 }}>
            {[
              { val: "5K+", label: "Игроков" },
              { val: "12K+", label: "Анкет" },
              { val: "98%", label: "Анонимность" },
            ].map(s => (
              <div key={s.label} className="text-center">
                <div className="font-orbitron font-black text-2xl neon-text-pink">{s.val}</div>
                <div className="text-white/50 text-xs font-rubik mt-1">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Разделитель */}
      <div className="avakin-divider mx-6 mb-0" />

      {/* HERO IMAGE */}
      <section className="relative z-10 py-16 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="relative rounded-2xl overflow-hidden neon-border-purple animate-float">
            <img src={HERO_IMG} alt="AvaMatch" className="w-full object-cover" style={{ maxHeight: 420 }} />
            <div className="absolute inset-0" style={{
              background: "linear-gradient(to top, rgba(10,5,20,0.9) 0%, transparent 50%)"
            }} />
            <div className="absolute bottom-6 left-6 right-6">
              <div className="font-orbitron font-bold text-2xl text-white mb-1">Найди своего игрока</div>
              <div className="text-white/60 text-sm font-rubik">Тысячи анкет ждут тебя в мире Avakin Life</div>
            </div>
            <div className="absolute top-4 right-4 glass-card neon-border-pink px-3 py-1 rounded-full text-xs font-orbitron text-white/90">
              ❤️ Match
            </div>
          </div>
        </div>
      </section>

      {/* ФУНКЦИИ */}
      <section id="Функции" className="relative z-10 py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <div className="font-orbitron text-xs tracking-[0.3em] mb-3 neon-text-cyan">ВОЗМОЖНОСТИ БОТА</div>
            <h2 className="font-orbitron font-black text-4xl text-white mb-4">Всё что нужно для<br /><span className="neon-text-purple">знакомств в игре</span></h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f, i) => {
              const c = colorMap[f.color as ColorType];
              return (
                <div key={i}
                  className={`glass-card ${c.border} rounded-2xl p-6 hover:scale-[1.02] transition-all duration-300 cursor-default`}>
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                    style={{ background: c.bg }}>
                    <Icon name={f.icon} size={22} className={c.text} />
                  </div>
                  <h3 className={`font-orbitron font-bold text-base mb-2 ${c.text}`}>{f.title}</h3>
                  <p className="text-white/60 text-sm font-rubik leading-relaxed">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* КАК РАБОТАЕТ */}
      <section id="Как работает" className="relative z-10 py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <div className="font-orbitron text-xs tracking-[0.3em] mb-3 neon-text-pink">ИНСТРУКЦИЯ</div>
            <h2 className="font-orbitron font-black text-4xl text-white">4 простых шага<br /><span className="neon-text-cyan">до первого чата</span></h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {steps.map((s, i) => (
              <div key={i} className="relative glass-card rounded-2xl p-6 text-center">
                <div className="font-orbitron font-black text-5xl mb-3" style={{
                  background: "linear-gradient(135deg, #ff2d9b, #b829ff)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                }}>
                  {s.num}
                </div>
                <h3 className="font-orbitron font-bold text-sm text-white mb-2">{s.title}</h3>
                <p className="text-white/55 text-xs font-rubik leading-relaxed">{s.desc}</p>
                {i < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-3 z-10">
                    <Icon name="ChevronRight" size={20} className="neon-text-purple" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* АНКЕТЫ — ДЕМО */}
      <section id="Анкеты" className="relative z-10 py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <div className="font-orbitron text-xs tracking-[0.3em] mb-3" style={{ color: "var(--neon-gold)", textShadow: "0 0 10px var(--neon-gold)" }}>ДЕМО АНКЕТ</div>
            <h2 className="font-orbitron font-black text-4xl text-white">Профили<br /><span className="neon-text-pink">игроков</span></h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {profiles.map((p, i) => (
              <div key={i}
                className={`glass-card rounded-2xl p-5 cursor-pointer transition-all duration-300 ${activeProfile === i ? "neon-border-pink scale-[1.03]" : "border border-white/8 hover:border-white/15"}`}
                onClick={() => setActiveProfile(i)}>
                <div className="w-20 h-20 rounded-2xl flex items-center justify-center text-4xl mx-auto mb-4"
                  style={{ background: "linear-gradient(135deg, rgba(184,41,255,0.3), rgba(255,45,155,0.3))", border: "1px solid rgba(255,45,155,0.3)" }}>
                  {p.emoji}
                </div>
                <div className="text-center">
                  <div className="font-orbitron font-bold text-sm text-white mb-1">{p.name}</div>
                  <div className="text-white/50 text-xs font-rubik mb-3">{p.gender} · {p.age} лет · {p.orientation}</div>
                  <div className="flex items-center justify-center gap-4">
                    <button
                      onClick={e => { e.stopPropagation(); handleLike(i); }}
                      className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-orbitron transition-all ${liked[i] ? "bg-pink-500/30 neon-text-pink" : "bg-white/5 text-white/40 hover:bg-white/10"}`}>
                      <Icon name="Heart" size={12} />
                      {p.likes + (liked[i] ? 1 : 0)}
                    </button>
                    <button className="flex items-center gap-1 px-3 py-1 rounded-full text-xs font-orbitron bg-white/5 text-white/40 hover:bg-white/10 transition-all">
                      <Icon name="ThumbsDown" size={12} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-10">
            <p className="text-white/40 text-xs font-rubik mb-4">* Демо-версия. Реальные анкеты доступны только в Telegram</p>
            <a href="https://t.me/AvaMatchBot" target="_blank" rel="noopener noreferrer"
              className="btn-neon-pink px-8 py-3 rounded-full font-orbitron font-bold text-white text-sm tracking-wide inline-flex items-center gap-2">
              <Icon name="Send" size={16} />
              Смотреть все анкеты
            </a>
          </div>
        </div>
      </section>

      {/* БЕЗОПАСНОСТЬ */}
      <section className="relative z-10 py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="glass-card neon-border-cyan rounded-3xl p-8 md:p-12">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
              <div>
                <div className="neon-text-cyan font-orbitron text-xs tracking-[0.3em] mb-3">БЕЗОПАСНОСТЬ</div>
                <h2 className="font-orbitron font-black text-3xl text-white mb-6">Защита на<br /><span className="neon-text-cyan">каждом уровне</span></h2>
                <div className="space-y-4">
                  {[
                    { icon: "ShieldCheck", text: "Скрытие ID — никто не узнает твой Telegram" },
                    { icon: "Filter", text: "Автофильтрация нецензурной лексики" },
                    { icon: "Ban", text: "Автоблокировка после 3 жалоб" },
                    { icon: "Flag", text: "Кнопка жалобы в каждом чате" },
                    { icon: "Star", text: "Система рейтинга и отзывов" },
                  ].map((item, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                        style={{ background: "rgba(0,212,255,0.15)" }}>
                        <Icon name={item.icon} size={16} className="neon-text-cyan" />
                      </div>
                      <span className="text-white/75 text-sm font-rubik">{item.text}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="text-center">
                <div className="w-40 h-40 rounded-full flex items-center justify-center mx-auto mb-4 relative"
                  style={{ background: "radial-gradient(circle, rgba(0,212,255,0.2) 0%, transparent 70%)" }}>
                  <div className="absolute inset-0 rounded-full neon-border-cyan animate-pulse-neon" />
                  <Icon name="Shield" size={64} className="neon-text-cyan" />
                </div>
                <div className="font-orbitron font-black text-3xl neon-text-cyan mb-1">100%</div>
                <div className="text-white/50 text-sm font-rubik">Анонимность гарантирована</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative z-10 py-24 px-6 text-center">
        <div className="max-w-3xl mx-auto">
          <div className="font-orbitron font-black text-5xl md:text-6xl text-white mb-6">
            Готов найти<br /><span className="neon-text-pink">своего игрока?</span>
          </div>
          <p className="text-white/55 font-rubik text-lg mb-10">
            Присоединяйся к тысячам игроков Avakin Life прямо сейчас — бесплатно и анонимно
          </p>
          <a href="https://t.me/AvaMatchBot" target="_blank" rel="noopener noreferrer"
            className="btn-neon-pink px-10 py-5 rounded-full font-orbitron font-black text-white text-base tracking-wide inline-flex items-center gap-3">
            <Icon name="Send" size={22} />
            Открыть AvaMatch в Telegram
          </a>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="relative z-10 px-6 py-10 border-t border-white/5">
        <div className="max-w-6xl mx-auto">
          <div className="avakin-divider mb-8" />
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full flex items-center justify-center"
                style={{ background: "linear-gradient(135deg, #ff2d9b, #b829ff)" }}>
                <span className="text-white text-sm font-bold font-orbitron">A</span>
              </div>
              <span className="font-orbitron font-bold text-sm tracking-widest neon-text-pink">AVA<span className="neon-text-cyan">MATCH</span></span>
            </div>
            <div className="flex items-center gap-6">
              {["Правила", "Конфиденциальность", "Поддержка"].map(link => (
                <a key={link} href="#" className="text-white/35 hover:text-white/70 text-xs font-rubik transition-colors">{link}</a>
              ))}
            </div>
            <div className="text-white/25 text-xs font-rubik">© 2026 AvaMatch · Не является официальным ботом Avakin Life</div>
          </div>
        </div>
      </footer>
    </div>
  );
}