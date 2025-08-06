<script lang="ts">
	import { PUBLIC_API_URL } from '$env/static/public';
	const API_BASE = `${PUBLIC_API_URL}/api/v1`;

	const ACCEPTED_TYPES = [
		'image/jpeg',
		'image/png',
		'image/gif',
		'application/pdf',
		'application/msword',
		'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
		'video/mp4',
		'video/quicktime'
	];

	let dragOver = false;
	let selectedFile: File | null = null;
	let message: { type: string; text: string } | null = null;

	const uploadFile = async (file: File) => {
		if (!ACCEPTED_TYPES.includes(file.type)) {
			message = { type: 'error', text: 'File type not supported.' };
			return;
		}

		const formData = new FormData();
		formData.append('file', file);

		message = { type: 'info', text: 'Uploading...' };

		try {
			const res = await fetch(`${API_BASE}/upload`, {
				method: 'POST',
				body: formData
			});
			if (!res.ok) throw new Error(await res.text());
			message = { type: 'success', text: 'Upload successful!' };
		} catch (err) {
			message = { type: 'error', text: 'Upload failed.' };
			console.error(err);
		}
	};

	const handleDrop = async (event: DragEvent) => {
		event.preventDefault();
		dragOver = false;
		const files = event.dataTransfer?.files;
		if (files && files.length > 0) {
			selectedFile = files[0];
			await uploadFile(selectedFile);
		}
	};

	const handleFileChange = async (event: Event) => {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];
		if (file) {
			selectedFile = file;
			await uploadFile(file);
		}
	};

	import { onMount } from 'svelte';

	type FileMeta = {
		_id: string;
		filename: string;
		s3_path: string;
		content_type: string;
		upload_date: string;
	};

	let files: FileMeta[] = [];

	onMount(async () => {
		const res = await fetch(`${API_BASE}/files`);
		files = await res.json();
	});
</script>

<div class="p-6">
	<h1 class="mb-4 text-center text-2xl font-bold">File Upload</h1>
	<div
		role="region"
		class="cursor-pointer rounded-md border-2 border-dashed border-gray-400 p-6 text-center {dragOver
			? 'bg-gray-100'
			: ''}"
		on:dragover|preventDefault={() => (dragOver = true)}
		on:dragleave={() => (dragOver = false)}
		on:drop={handleDrop}
	>
		<p>Drag & drop a file here</p>
		<p>or</p>
		<input
			type="file"
			accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.mp4,.mov"
			on:change={handleFileChange}
		/>
	</div>

	{#if message}
		<p
			class="mt-4 rounded p-2 text-center text-sm {message.type == 'error'
				? 'bg-red-100 text-red-600'
				: message.type == 'success'
					? 'bg-green-100 text-green-600'
					: 'bg-gray-100 text-gray-600'}"
		>
			{message.text}
		</p>
	{/if}

	{#if files.length}
		<table class="mt-6 w-full table-auto border border-gray-200">
			<thead class="bg-gray-100 text-left">
				<tr>
					<th class="p-2">Filename</th>
					<th class="p-2">Type</th>
					<th class="p-2">Upload Date</th>
				</tr>
			</thead>
			<tbody>
				{#each files as file}
					<tr class="border-t">
						<td class="p-2">{file.filename}</td>
						<td class="p-2">{file.content_type}</td>
						<td class="p-2">{file.upload_date?.slice(0, 19).replace('T', ' ')}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<p class="mt-4 text-sm text-gray-500">No files uploaded yet.</p>
	{/if}
</div>
