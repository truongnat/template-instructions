/**
 * Mobile Bottom Navigation Bar
 * @module components/mobile/MobileNav
 */

import { motion } from 'framer-motion';
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
    { id: 'favorites', label: 'Favorites', icon: Star },
    { id: 'more', label: 'More', icon: MoreHorizontal },
];

export function MobileNav({ activeTab, onTabChange, onOpenDrawer }: MobileNavProps) {
    const { setFilterType, navigateToFolder } = useFileStore();

    const handleTabClick = (tab: NavTab) => {
        onTabChange(tab);

        switch (tab) {
            case 'home':
                navigateToFolder(null);
                setFilterType('all');
                break;
            case 'files':
                navigateToFolder(null);
                setFilterType('all');
                break;
            case 'favorites':
                // TODO: Implement favorites filter
                break;
            case 'more':
                onOpenDrawer();
                break;
        }
    };

    return (
        <nav
            className="fixed bottom-0 left-0 right-0 z-40 glass"
            style={{
                paddingBottom: 'env(safe-area-inset-bottom)',
                borderTop: '1px solid rgba(255, 255, 255, 0.1)',
            }}
        >
            <div className="flex items-center justify-around h-16">
                {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeTab === item.id;

                    return (
                        <button
                            key={item.id}
                            onClick={() => handleTabClick(item.id)}
                            className="flex flex-col items-center justify-center flex-1 h-full touch-target relative"
                        >
                            {/* Active indicator background */}
                            {isActive && (
                                <motion.div
                                    layoutId="nav-indicator"
                                    className="absolute inset-x-2 top-1.5 bottom-1.5 rounded-xl"
                                    style={{ background: 'rgba(124, 58, 237, 0.2)' }}
                                    transition={{ type: 'spring', bounce: 0.2, duration: 0.6 }}
                                />
                            )}

                            <motion.div
                                animate={{ scale: isActive ? 1.1 : 1 }}
                                className="relative z-10 flex flex-col items-center gap-0.5"
                            >
                                <Icon
                                    size={22}
                                    style={{
                                        color: isActive ? '#7c3aed' : 'rgba(255, 255, 255, 0.5)',
                                        transition: 'color 0.2s',
                                    }}
                                />
                                <span
                                    className="text-xs font-medium"
                                    style={{
                                        color: isActive ? '#7c3aed' : 'rgba(255, 255, 255, 0.5)',
                                        transition: 'color 0.2s',
                                    }}
                                >
                                    {item.label}
                                </span>
                            </motion.div>
                        </button>
                    );
                })}
            </div>

            {/* Floating Upload Button */}
            <motion.button
                onClick={triggerUpload}
                className="absolute -top-7 left-1/2 -translate-x-1/2 w-14 h-14 rounded-full flex items-center justify-center shadow-lg"
                style={{
                    background: 'linear-gradient(135deg, #7c3aed, #2563eb)',
                    boxShadow: '0 4px 20px rgba(124, 58, 237, 0.4)',
                }}
                whileTap={{ scale: 0.95 }}
                whileHover={{ scale: 1.05 }}
            >
                <Upload size={24} className="text-white" />
            </motion.button>
        </nav>
    );
}
