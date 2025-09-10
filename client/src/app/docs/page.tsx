"use client";

import { useState } from "react";
import FileUpload from "@/app/blocks/FileUpload";
import { Button } from "@/components/ui/button";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/components/ui/dialog";

const Docs = () => {
	const [open, setOpen] = useState(false);

	return (
		<div className="w-full h-full flex flex-col items-center justify-center">
			<p className="text-xl font-bold text-gray-700 mb-4">
				You haven&apos;t uploaded any files yet.
			</p>
			<p className="text-base text-gray-500 mb-6">
				Click the button below to upload files
			</p>

			<Dialog open={open} onOpenChange={setOpen}>
				<DialogTrigger asChild>
					<Button>Upload</Button>
				</DialogTrigger>
				<DialogContent className="max-w-2xl">
					<DialogHeader>
						<DialogTitle>Upload Files</DialogTitle>
						<DialogDescription>
							Select and upload your files to get started.
						</DialogDescription>
					</DialogHeader>
					<FileUpload />
				</DialogContent>
			</Dialog>
		</div>
	);
};

export default Docs;
