import aiohttp

async def get_file(urls, day):
    session = aiohttp.ClientSession(cookies=cookies, headers=headers)
    results = {}
    conc_req = 40
    await gather_with_concurrency(conc_req, *[get_async(i, session, results) for i in urls.values()])
    await session.close()
    Path("rashodilis").mkdir(parents=True, exist_ok=True)
    Path("rashodilis/{0}".format(day)).mkdir(parents=True, exist_ok=True)
    # writer = pd.ExcelWriter("files.xlsx", engine = 'openpyxl')
    for i, j in results.items():
        with open(f'./rashodilis/{day}/{i}', "wb+") as f:
            f.write(j)


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))


def get_filename(response):
    header = response.headers.get('Content-Disposition')
    if not header:
        return False
    filename = re.findall(r"filename\*=UTF-8''(.+)", header)
    filename = unquote(filename[0])
    return str(filename)


async def get_async(url, session, results):
    async with session.get(url) as response:
        # i = url.split('=')[-1]
        if response.status == 200:
            obj = await response.read()
            filename = get_filename(response)
            results[filename] = obj