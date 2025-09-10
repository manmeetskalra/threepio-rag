import type { Metadata } from "next";
import React from "react";

import { AppSidebar } from "@/components/app-sidebar";
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarGroup,
	SidebarGroupContent,
	SidebarHeader,
	SidebarInput,
} from "@/components/ui/sidebar";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { NavUser } from "@/components/nav-user";

// This layout owns the second sidebar for chat-only routes
export const metadata: Metadata = {
	title: "Chat",
};

const sampleUser = {
	name: "shadcn",
	email: "m@example.com",
	avatar: "/avatars/shadcn.jpg",
};

export default function ChatLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<div className="flex h-screen w-full">
			{/* First/sidebar-icons only comes from AppSidebar in root layout */}
			{/* This is the second sidebar dedicated to chat */}
			<Sidebar collapsible="none" className="hidden w-[350px] md:flex">
				<SidebarHeader className="gap-3.5 border-b p-4">
					<div className="flex w-full items-center justify-between">
						<div className="text-foreground text-base font-medium">Chat</div>
						<Label className="flex items-center gap-2 text-sm">
							<span>Unreads</span>
							<Switch className="shadow-none" />
						</Label>
					</div>
					<SidebarInput placeholder="Type to search..." />
				</SidebarHeader>
				<SidebarContent>
					<SidebarGroup className="px-0">
						<SidebarGroupContent>
							{/* Chat list or other chat-specific content could go here. */}
						</SidebarGroupContent>
					</SidebarGroup>
				</SidebarContent>
				<SidebarFooter>
					<NavUser user={sampleUser} />
				</SidebarFooter>
			</Sidebar>

			{/* Main chat content */}
			{children}
		</div>
	);
}
