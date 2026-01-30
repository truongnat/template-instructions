/**
 * Mobile Bottom Navigation Bar - Updated with CSS Animations
 * @module components/mobile/MobileNav
 */

import { Home, FolderOpen, Star, MoreHorizontal, Upload } from 'lucide-react';
import { useFileStore } from '../../store/files';
import { triggerUpload } from '../upload/DropZone';

type NavTab = 'home' | 'files' | 'favorites' | 'more';

interface MobileNavProps {
    activeTab: NavTab;
    onTabChange: (tab: NavTab) => void;
    onOpenDrawer: () => void;
}

const navItems: { id: NavTab; label: string; icon: typeof Home }[] = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'files', label: 'Files', icon: FolderOpen },
    { id: 'favorites', label: 'Starred', icon: Star },
    { id: 'more', label: 'Menu', icon: MoreHorizontal },
];

export function MobileNav({ activeTab, onTabChange, onOpenDrawer }: MobileNavProps) {
    const { setFilterType, navigateToFolder } = useFileStore();

    const handleTabClick = (tab: NavTab) => {
        onTabChange(tab);

        switch (tab) {
            case 'home':
            case 'files':
                navigateToFolder(null);
                setFilterType('all');
                break;
            case 'favorites':
                // TODO: Favorites
                break;
            case 'more':
                onOpenDrawer();
                break;
        }
    };

    return (
        <nav
            className="fixed bottom-0 left-0 right-0 z-40 glass safe-bottom"
            style={{ borderTop: '1px solid rgba(255, 255, 255, 0.05)' }}
        >
            <div className="flex items-center justify-between h-16 px-2">
                {navItems.map((item, index) => {
                    const Icon = item.icon;
                    const isActive = activeTab === item.id;

                    // Add spacer for the center FAB
                    const isSecond = index === 1;

                    return (
                        <div key={item.id} className="flex flex-1 items-center justify-center">
                            <button
                                onClick={() => handleTabClick(item.id)}
                                className={`flex flex-col items-center justify-center gap-1 w-full h-full transition-all duration-300 ${isActive ? 'text-accent-purple' : 'text-white/30 hover:text-white/50'
                                    }`}
                            >
                                <div className={`p-2 rounded-xl transition-all duration-300 ${isActive ? 'bg-accent-purple/10' : ''}`}>
                                    <Icon size={22} className={isActive ? 'animate-scale-in' : ''} />
                                </div>
                                <span className={`text-[10px] font-black uppercase tracking-widest transition-opacity ${isActive ? 'opacity-100' : 'opacity-40'}`}>
                                    {item.label}
                                </span>
                            </button>

                            {/* Insert FAB in the middle */}
                            {isSecond && (
                                <div className="flex-1 flex justify-center -translate-y-8 animate-fade-in">
                                    <button
                                        onClick={triggerUpload}
                                        className="w-14 h-14 rounded-2xl bg-gradient-to-br from-accent-purple to-accent-blue flex items-center justify-center shadow-2xl shadow-accent-purple/40 border border-white/20 active:scale-90 transition-transform hover:rotate-90 duration-500"
                                    >
                                        <Upload size={24} className="text-white" />
                                    </button>
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </nav>
    );
}
