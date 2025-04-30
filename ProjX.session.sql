SELECT 
    p.project_id,
    p.project_name,
    p.status,
    u.name AS project_leaderSELECT 
    p.project_id,
    p.project_name,
    p.status,
    u.name AS project_leader
FROM 
    projects p
JOIN 
    project_members pm ON p.project_id = pm.project_id AND pm.is_leader = TRUE
JOIN 
    users u ON pm.user_id = u.user_id
WHERE 
    p.status = 'Ongoing';
FROM 
    projects p
JOIN 
    project_members pm ON p.project_id = pm.project_id AND pm.is_leader = TRUE
JOIN 
    users u ON pm.user_id = u.user_id
WHERE 
    p.status = 'Ongoing';
