function [val, vec] = calc_eig(D, W)
	L = D - W;
	[e_val, e_vec] = eig(L);
	val = e_val
	vec = e_vec
