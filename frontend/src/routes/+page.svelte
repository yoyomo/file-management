<script lang="ts">
	import { PUBLIC_API_URL } from '$env/static/public';

	import { onMount } from 'svelte';

	type FileMeta = {
		_id: string;
		filename: string;
		s3_path: string;
		content_type: string;
		upload_date: string;
		size: number;
	};

	let files: FileMeta[] = [];

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

	onMount(async () => {
		const res = await fetch(`${API_BASE}/files`);
		files = await res.json();
	});

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
			const uploaded = await res.json();
			files = [...files, uploaded];
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

	const renameFile = async (file: FileMeta) => {
		const res = await fetch(`${API_BASE}/files/${file._id}`, {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ filename: file.filename })
		});
		if (res.ok) {
			message = { type: 'success', text: 'Rename successful!' };
		} else {
			message = { type: 'error', text: 'Rename failed.' };
		}
	};

	const deleteFile = async (id: string) => {
		await fetch(`${API_BASE}/files/${id}`, { method: 'DELETE' });
		files = files.filter((f) => f._id !== id);
		message = { type: 'success', text: 'File deleted successfully!' };
	};

	const downloadFile = async (id: string) => {
		const res = await fetch(`${API_BASE}/files/${id}/download`);
		const { url } = await res.json();
		window.open(url, '_blank');
		if (res.ok) {
			message = { type: 'success', text: 'Download successful!' };
		} else {
			message = { type: 'error', text: 'Download failed.' };
		}
	};

	let fileInput: HTMLInputElement;

	const humanFileSize = (bytes: number, decimals = 1) => {
		if (bytes === 0) return '0 B';
		const k = 1024;
		const dm = decimals < 0 ? 0 : decimals;
		const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
	};
</script>

<div class="p-6">
	<h1 class="mb-4 text-center text-2xl font-bold">File Upload</h1>
	<button
		type="button"
		tabindex="0"
		class="w-full cursor-pointer rounded-md border-2 border-dashed border-gray-400 p-6 text-center {dragOver
			? 'bg-gray-100'
			: ''}"
		on:dragover|preventDefault={() => (dragOver = true)}
		on:dragleave={() => (dragOver = false)}
		on:drop={handleDrop}
		on:click={() => fileInput.click()}
		on:keydown={(e) => {
			if (e.key === 'Enter' || e.key === ' ') {
				fileInput.click();
			}
		}}
		style="user-select: none;"
	>
		<p>Drag & drop a file here</p>
		<p>or</p>
		<input
			bind:this={fileInput}
			type="file"
			accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.mp4,.mov"
			on:change={handleFileChange}
			style="display: none;"
		/>
		<span class="mt-2 inline-block rounded bg-gray-500 px-4 py-2 text-white hover:bg-gray-600">
			Browse
		</span>
	</button>

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
					<th class="p-2">Size</th>
					<th class="p-2">Type</th>
					<th class="p-2">Upload Date</th>
					<th class="p-2">Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each files as file}
					<tr class="border-t">
						<td class="p-2"
							><input
								type="text"
								class="w-full rounded border px-2 py-1"
								bind:value={file.filename}
								on:change={() => renameFile(file)}
							/></td
						>
						<td class="p-2">{humanFileSize(file.size)}</td>
						<td class="p-2">{file.content_type}</td>
						<td class="p-2">{file.upload_date?.slice(0, 19).replace('T', ' ')}</td>
						<td class="p-2">
							<button
								class="mt-2 inline-block cursor-pointer rounded bg-red-500 px-4 py-2 text-white hover:bg-red-600"
								on:click={() => {
									if (confirm(`Delete ${file.filename}?`)) {
										deleteFile(file._id);
									}
								}}
							>
								Delete
							</button>
							<button
								class="mt-2 inline-block cursor-pointer rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
								on:click={() => downloadFile(file._id)}
							>
								Download
							</button>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{:else}
		<p class="mt-4 text-sm text-gray-500">No files uploaded yet.</p>
	{/if}
</div>
