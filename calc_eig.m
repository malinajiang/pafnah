function [val, vec] = calc_eig(D, W)
	L = D - W;
	[val, vec] = eig(L);
