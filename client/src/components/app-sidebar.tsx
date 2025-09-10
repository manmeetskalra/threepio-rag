"use client";

import * as React from "react";
import { MessageCircle, Command, File } from "lucide-react";
import { useRouter } from "next/navigation";

import { NavUser } from "@/components/nav-user";
import {
	Sidebar,
	SidebarContent,
	SidebarFooter,
	SidebarGroup,
	SidebarGroupContent,
	SidebarHeader,
	SidebarMenu,
	SidebarMenuButton,
	SidebarMenuItem,
	useSidebar,
} from "@/components/ui/sidebar";

// This is sample data
const data = {
	user: {
		name: "shadcn",
		email: "m@example.com",
		avatar: "/avatars/shadcn.jpg",
	},
	navMain: [
		{
			title: "Chat",
			url: "/",
			icon: MessageCircle,
			isActive: true,
		},
		{
			title: "Docs",
			url: "/docs",
			icon: File,
			isActive: false,
		},
	],
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
	// Note: I'm using state to show active item.
	// IRL you should use the url/router.
	const [activeItem, setActiveItem] = React.useState(data.navMain[0]);
	const { setOpen } = useSidebar();
	const router = useRouter();

	return (
		<Sidebar
			collapsible="none"
			className="w-[calc(var(--sidebar-width-icon)+1px)]! border-r"
			{...props}
		>
			<SidebarHeader>
				<SidebarMenu>
					<SidebarMenuItem>
						<SidebarMenuButton size="lg" asChild className="md:h-8 md:p-0">
							<a href="#">
								<div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
									<Command className="size-4" />
								</div>
								<div className="grid flex-1 text-left text-sm leading-tight">
									<span className="truncate font-medium">Acme Inc</span>
									<span className="truncate text-xs">Enterprise</span>
								</div>
							</a>
						</SidebarMenuButton>
					</SidebarMenuItem>
				</SidebarMenu>
			</SidebarHeader>
			<SidebarContent>
				<SidebarGroup>
					<SidebarGroupContent className="px-1.5 md:px-0">
						<SidebarMenu>
							{data.navMain.map((item) => (
								<SidebarMenuItem key={item.title}>
									<SidebarMenuButton
										tooltip={{
											children: item.title,
											hidden: false,
										}}
										onClick={() => {
											setActiveItem(item);
											router.push(item.url || "/");
											setOpen(true);
										}}
										isActive={activeItem?.title === item.title}
										className="px-2.5 md:px-2"
									>
										<item.icon />
										<span>{item.title}</span>
									</SidebarMenuButton>
								</SidebarMenuItem>
							))}
						</SidebarMenu>
					</SidebarGroupContent>
				</SidebarGroup>
			</SidebarContent>
			<SidebarFooter>
				<NavUser user={data.user} />
			</SidebarFooter>
		</Sidebar>
	);
}
