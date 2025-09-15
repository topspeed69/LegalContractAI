import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import ThemeToggle from "@/components/ThemeToggle";
import { useAuth } from "@/contexts/AuthContext";
import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuTrigger,
  NavigationMenuContent,
} from "@/components/ui/navigation-menu";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  User,
  Settings,
  LogOut,
  GavelIcon,
  Menu as MenuIcon,
  FileText,
  File,
  CheckCircle,
  PenSquare,
} from "lucide-react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";

const Header: React.FC = () => {
  const { user, signOut } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleSignOut = async () => {
    await signOut();
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container-tight h-16 flex items-center justify-between">
  <Link to={user ? "/dashboard" : "/"} className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center text-white dark:bg-[hsl(var(--highlight))]">
            <GavelIcon className="h-5 w-5" />
          </div>
          <span className="font-semibold text-lg">LegalAssist</span>
        </Link>

        <div className="flex items-center gap-6">
          <nav className="hidden md:flex items-center gap-2">
            <NavigationMenu>
              <NavigationMenuList>
                <NavigationMenuItem>
                  <NavigationMenuTrigger className="h-10 text-base font-medium">Services</NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <div className="grid grid-cols-2 gap-2 p-4 w-[400px]">
                      <Link 
                        to="/case-summary" 
                        className="block rounded-md p-3 hover:bg-accent dark:hover:bg-accent/30 transition-colors"
                      >
                        <div className="font-medium text-sm mb-1">Case Summarization</div>
                        <p className="text-xs text-muted-foreground">Generate concise summaries</p>
                      </Link>
                      <Link 
                        to="/loophole-detection" 
                        className="block rounded-md p-3 hover:bg-accent dark:hover:bg-accent/30 transition-colors"
                      >
                        <div className="font-medium text-sm mb-1">Loophole Detection</div>
                        <p className="text-xs text-muted-foreground">Identify legal risks</p>
                      </Link>
                      <Link 
                        to="/clause-classification" 
                        className="block rounded-md p-3 hover:bg-accent dark:hover:bg-accent/30 transition-colors"
                      >
                        <div className="font-medium text-sm mb-1">Clause Classification</div>
                        <p className="text-xs text-muted-foreground">Analyze clauses</p>
                      </Link>
                      <Link 
                        to="/compliance-check" 
                        className="block rounded-md p-3 hover:bg-accent dark:hover:bg-accent/30 transition-colors"
                      >
                        <div className="font-medium text-sm mb-1">Compliance Checker</div>
                        <p className="text-xs text-muted-foreground">Check documents for compliance</p>
                      </Link>
                      <Link 
                        to="/contract-drafting" 
                        className="block rounded-md p-3 hover:bg-accent dark:hover:bg-accent/30 transition-colors"
                      >
                        <div className="font-medium text-sm mb-1">Contract Drafting</div>
                        <p className="text-xs text-muted-foreground">Create contracts with AI</p>
                      </Link>
                    </div>
                  </NavigationMenuContent>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <Link 
                    to="/about"
                    className={cn(
                      "h-10 px-4 flex items-center text-base font-medium rounded-md transition-colors",
                      location.pathname === "/about" 
                        ? "text-primary dark:text-[hsl(var(--highlight))]" 
                        : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    About
                  </Link>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <Link 
                    to="/pricing"
                    className={cn(
                      "h-10 px-4 flex items-center text-base font-medium rounded-md transition-colors",
                      location.pathname === "/pricing" 
                        ? "text-primary dark:text-[hsl(var(--highlight))]" 
                        : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    Pricing
                  </Link>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <Link 
                    to="/contact"
                    className={cn(
                      "h-10 px-4 flex items-center text-base font-medium rounded-md transition-colors",
                      location.pathname === "/contact" 
                        ? "text-primary dark:text-[hsl(var(--highlight))]" 
                        : "text-muted-foreground hover:text-foreground"
                    )}
                  >
                    Contact
                  </Link>
                </NavigationMenuItem>
              </NavigationMenuList>
            </NavigationMenu>
          </nav>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                    <Avatar className="h-9 w-9">
                      <AvatarImage src={user.user_metadata.avatar_url} alt={user.user_metadata.full_name || 'User'} />
                      <AvatarFallback>{(user.user_metadata.full_name || 'User').charAt(0).toUpperCase()}</AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user.user_metadata.full_name}</p>
                      <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link to="/profile" className="flex items-center">
                      <User className="mr-2 h-4 w-4" />
                      <span>Profile</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/settings" className="flex items-center">
                      <Settings className="mr-2 h-4 w-4" />
                      <span>Settings</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/activity-history" className="flex items-center">
                      <FileText className="mr-2 h-4 w-4" />
                      <span>My activity</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/dashboard" className="flex items-center">
                      <span className="mr-2 h-4 w-4">🏠</span>
                      <span>Dashboard</span>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleSignOut} className="flex items-center">
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="hidden md:flex items-center gap-2">
                <Button variant="ghost" asChild className="h-10 px-4 text-base">
                  <Link to="/login">Log in</Link>
                </Button>
                <Button asChild className="h-10 px-4 text-base">
                  <Link to="/signup">Sign up</Link>
                </Button>
              </div>
            )}

            {/* Mobile menu */}
            <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
              <SheetTrigger asChild className="md:hidden">
                <Button variant="ghost" size="icon" className="h-10 w-10">
                  <MenuIcon className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent>
                <div className="flex flex-col space-y-4">
                  <div className="font-medium mb-2">Menu</div>
                  <nav className="flex flex-col space-y-2">
                    <div className="py-2">
                      <div className="font-medium text-sm mb-2">Services</div>
                      <div className="pl-2 flex flex-col space-y-2">
                        <Link to="/case-summary" className="text-sm text-muted-foreground hover:text-foreground" onClick={() => setMobileMenuOpen(false)}>
                          Case Summarization
                        </Link>
                        <Link to="/loophole-detection" className="text-sm text-muted-foreground hover:text-foreground" onClick={() => setMobileMenuOpen(false)}>
                          Loophole Detection
                        </Link>
                        <Link to="/clause-classification" className="text-sm text-muted-foreground hover:text-foreground" onClick={() => setMobileMenuOpen(false)}>
                          Clause Classification
                        </Link>
                            <Link to="/compliance-check" className="text-sm text-muted-foreground hover:text-foreground" onClick={() => setMobileMenuOpen(false)}>
                              Compliance Checker
                            </Link>
                        <Link to="/contract-drafting" className="text-sm text-muted-foreground hover:text-foreground" onClick={() => setMobileMenuOpen(false)}>
                          Contract Drafting
                        </Link>
                      </div>
                    </div>

                    <Link to="/about" className="text-sm text-muted-foreground hover:text-foreground" onClick={() => setMobileMenuOpen(false)}>
                      About
                    </Link>
                    <Link to="/pricing" className="text-sm text-muted-foreground hover:text-foreground" onClick={() => setMobileMenuOpen(false)}>
                      Pricing
                    </Link>
                    <Link to="/contact" className="text-sm text-muted-foreground hover:text-foreground" onClick={() => setMobileMenuOpen(false)}>
                      Contact
                    </Link>
                  </nav>

                  {!user && (
                    <div className="pt-4 space-y-2">
                      <Button variant="ghost" asChild className="w-full justify-center h-8 text-sm">
                        <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                          Log in
                        </Link>
                      </Button>
                      <Button asChild className="w-full justify-center h-8 text-sm">
                        <Link to="/signup" onClick={() => setMobileMenuOpen(false)}>
                          Sign up
                        </Link>
                      </Button>
                    </div>
                  )}
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
