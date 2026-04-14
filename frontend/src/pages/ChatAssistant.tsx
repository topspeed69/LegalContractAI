import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, Send, Bot, User, ArrowRight } from "lucide-react";
import { aiClient } from "@/lib/ai-clients";
import { cn } from "@/lib/utils";
import { Link } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { recordUsage } from "@/services/usage";

interface Message {
    role: 'user' | 'assistant';
    content: string;
    intent?: string;
    suggested_action?: string;
    citations?: {
        title: string;
        source: string;
        text: string;
    }[];
    id: string;
}

const ChatAssistant = () => {
    const { user } = useAuth();
    const [messages, setMessages] = useState<Message[]>([
        {
            id: 'initial',
            role: 'assistant',
            content: "Hello! I'm your LegalAssist advisor. I can help you navigate our platform and find the right tools. How can I assist you today?"
        }
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        if (messagesEndRef.current) {
            const viewport = messagesEndRef.current.closest('[data-radix-scroll-area-viewport]');
            if (viewport) {
                viewport.scrollTo({
                    top: viewport.scrollHeight,
                    behavior: "smooth"
                });
            } else {
                // Fallback for non-radix scroll areas
                messagesEndRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
            }
        }
    };

    useEffect(() => {
        const loadHistory = async () => {
            if (user) {
                const history = await aiClient.getHistory(user.id);
                if (history && history.length > 0) {
                    setMessages([
                        {
                            id: 'initial',
                            role: 'assistant',
                            content: "Hello! I'm your LegalAssist advisor. I can help you navigate our platform and find the right tools. How can I assist you today?"
                        },
                        ...history.map((m: any) => ({
                            id: m.id,
                            role: m.role,
                            content: m.content,
                            created_at: m.created_at
                        }))
                    ]);
                }
            }
        };
        loadHistory();
    }, [user]);

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSend = async (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMsg = input.trim();
        const userMsgId = crypto.randomUUID();
        setInput("");
        setMessages(prev => [...prev, { id: userMsgId, role: 'user', content: userMsg }]);
        setIsLoading(true);

        try {
            const response = await aiClient.process('chat-assistant', userMsg, { userId: user?.id });

            if (response.error) throw response.error;

            const reply = response.data || "I'm sorry, I couldn't process that.";
            const intent = response.metadata?.intent;
            const rawAction = (response.metadata as any)?.suggested_action;
            // Sanitize: only accept valid route paths, filter out "null" string and garbage
            const action = (rawAction && rawAction !== "null" && rawAction.startsWith("/")) ? rawAction : undefined;
            const citations = (response.metadata as any)?.citations;
            const assistantMsgId = crypto.randomUUID();

            const assistantMsg: Message = {
                id: assistantMsgId,
                role: 'assistant',
                content: reply,
                intent,
                suggested_action: action,
                citations: citations
            };

            setMessages(prev => [...prev, assistantMsg]);
        } catch (error) {
            console.error("Chat Error:", error);
            setMessages(prev => [
                ...prev,
                { id: crypto.randomUUID(), role: 'assistant', content: "Sorry, I encountered an error connecting to the AI assistant. Please try again later." }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="legal-bg py-10 px-4 sm:px-6 lg:px-8 min-h-screen flex items-center justify-center">
            <Card className="w-full max-w-4xl h-[80vh] flex flex-col shadow-2xl animate-fade-in border-primary/10">
                <div className="p-6 border-b bg-card rounded-t-xl flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
                        <Bot className="h-6 w-6" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold">Legal Advisor</h1>
                        <p className="text-sm text-muted-foreground">Ask for guidance on platform features</p>
                    </div>
                </div>

                <ScrollArea className="flex-1 p-6">
                    <div className="space-y-6">
                        {messages.map((msg) => (
                            <div key={msg.id} className={cn("flex gap-3", msg.role === 'user' ? "flex-row-reverse" : "")}>
                                <div className={cn(
                                    "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                                    msg.role === 'user' ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                                )}>
                                    {msg.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                                </div>
                                <div className={cn(
                                    "rounded-2xl px-4 py-3 max-w-[80%] text-sm",
                                    msg.role === 'user'
                                        ? "bg-primary text-primary-foreground rounded-tr-sm"
                                        : "bg-muted/50 border rounded-tl-sm"
                                )}>
                                    <p className="whitespace-pre-wrap">{msg.content}</p>

                                    {msg.citations && msg.citations.length > 0 && (
                                        <div className="mt-4 pt-3 border-t border-border/20 space-y-3">
                                            <p className="text-[10px] uppercase tracking-wider font-bold opacity-50">Legal Citations:</p>
                                            <div className="grid gap-2">
                                                {msg.citations.map((cite, cIdx) => (
                                                    <div key={cIdx} className="bg-background/50 p-2 rounded border border-border/10 text-[11px]">
                                                        <div className="font-semibold text-primary/80 mb-1">{cite.title}</div>
                                                        <div className="opacity-70 line-clamp-2 italic">"{cite.text}"</div>
                                                        <div className="mt-1 text-[9px] opacity-40">Source: {cite.source}</div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {msg.suggested_action && (
                                        <div className="mt-3 pt-3 border-t border-border/20">
                                            <p className="text-xs opacity-70 mb-2">Suggested Action:</p>
                                            <Button asChild size="sm" variant="secondary" className="w-full justify-between">
                                                <Link to={msg.suggested_action}>
                                                    Open Feature <ArrowRight className="h-3 w-3 ml-2" />
                                                </Link>
                                            </Button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex gap-3">
                                <div className="w-8 h-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center shrink-0">
                                    <Bot className="h-4 w-4" />
                                </div>
                                <div className="bg-muted/50 border rounded-2xl rounded-tl-sm px-4 py-3 flex items-center">
                                    <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                </ScrollArea>

                <div className="p-4 border-t bg-card rounded-b-xl">
                    <form onSubmit={handleSend} className="flex gap-2">
                        <Input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask for help..."
                            className="flex-1"
                            disabled={isLoading}
                        />
                        <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
                            <Send className="h-4 w-4" />
                        </Button>
                    </form>
                </div>
            </Card>
        </div>
    );
};

export default ChatAssistant;
